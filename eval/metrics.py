"""Per-day planning and scoring for the evaluation harness.

Every plan is scored on the day's OBSERVED values. Sensitivity runs use deep copies of the config;
the global config returned by load_config() is never mutated.
"""
import copy
import itertools

import numpy as np

from app.aqi import pm25_to_aqi
from app.baselines import b1, b2, b3_early, b3_late
from app.config import load_config
from app.exposure import day_arrays, exposure, plan_cost, slot_to_hhmm
from app.forecast import forecast
from app.models import DayRecord
from app.optimizer import optimize
from app.robust import robust_plan

CHALLENGERS = ("optimizer", "robust", "oracle")
BASELINES = ("B1", "B2", "b3_early", "b3_late")
PLANS = CHALLENGERS + BASELINES
PHYS = ("hours_ge_80f", "hours_ge_95f", "hours_aqi_ge_101", "hours_aqi_ge_151", "dual_hazard_hours", "paid_hours")
STRATA = ("heat_only", "smoke_only", "co_occurring", "mild")


def stratum(temp_f, aqi, cfg: dict | None = None) -> str:
    """Rule on OBSERVED data (config eval.strata): heat = max temp >= T, smoke = max AQI >= A."""
    s = (cfg or load_config())["eval"]["strata"]
    heat = float(np.max(temp_f)) >= s["heat_temp_f"]
    smoke = float(np.max(aqi)) >= s["smoke_aqi"]
    return {(True, False): "heat_only", (False, True): "smoke_only", (True, True): "co_occurring",
            (False, False): "mild"}[(heat, smoke)]


def forecast_arrays(day: DayRecord, pool: list[DayRecord], cfg: dict) -> tuple[np.ndarray, np.ndarray]:
    fc = forecast(day, pool, cfg=cfg)
    return np.asarray(fc.day.temp_f, dtype=float), pm25_to_aqi(fc.day.pm25_ugm3).aqi


def evaluable(pool: list[DayRecord], cfg: dict) -> list[DayRecord]:
    """ALL days that have a leakage-safe proxy forecast (enough prior history), in date order."""
    out = []
    for d in sorted(pool, key=lambda d: (d.provenance, d.date or "", d.id)):
        try:
            forecast(d, pool, cfg=cfg)
        except ValueError:
            continue
        out.append(d)
    return out


def score(blocks, ot, oa, cfg: dict) -> dict:
    m = exposure(ot, oa, blocks, cfg=cfg).model_dump()
    return {**{k: m[k] for k in PHYS}, "observed_cost": round(plan_cost(blocks, ot, oa, cfg=cfg), 6),
            "blocks": [f"{slot_to_hhmm(b.start_slot)}-{slot_to_hhmm(b.end_slot)}" for b in blocks]}


def evaluate_day(day: DayRecord, pool: list[DayRecord], cfg: dict) -> dict:
    ft, fa = forecast_arrays(day, pool, cfg)
    ot, oa = day_arrays(day)
    rob = robust_plan(day, pool, cfg=cfg)
    plans = {"optimizer": optimize(ft, fa, cfg=cfg), "robust": rob.plan,
             "oracle": optimize(ot, oa, cfg=cfg, name="oracle"),
             "B1": b1(ft, fa, cfg=cfg), "B2": b2(ft, fa, cfg=cfg),
             "b3_early": b3_early(ft, fa, cfg=cfg), "b3_late": b3_late(ft, fa, cfg=cfg)}
    return {"id": day.id, "date": day.date, "label": day.label, "provenance": day.provenance,
            "stratum": stratum(ot, oa, cfg), "robust_flags": rob.flags, "robust_uncertainty": rob.uncertainty,
            "plans": {k: score(p.blocks, ot, oa, cfg) for k, p in plans.items()}}


def classify_physical(a: dict, b: dict, cfg: dict) -> str:
    """PRIMARY outcome, a vs b on observed values. tie: every physical metric within tie_hours.
    win: no more hours >=95F and no more AQI>=101 hours, and strictly less on at least one.
    loss: the reverse. Otherwise 'mixed'."""
    th = cfg["eval"]["tie_hours"]
    if all(abs(a[k] - b[k]) < th for k in PHYS):
        return "tie"
    d95, d101 = a["hours_ge_95f"] - b["hours_ge_95f"], a["hours_aqi_ge_101"] - b["hours_aqi_ge_101"]
    if d95 < th and d101 < th and (d95 <= -th or d101 <= -th):
        return "win"
    if d95 > -th and d101 > -th and (d95 >= th or d101 >= th):
        return "loss"
    return "mixed"


def classify(a: dict, b: dict, cfg: dict) -> str:
    """SECONDARY outcome (uses the optimizer's own cost), a vs b on observed values: tie if every physical
    metric is within tie_hours and cost within tie_cost; otherwise win/loss by observed cost; 'mixed' if
    costs are equal but physical metrics differ."""
    e = cfg["eval"]
    dc = a["observed_cost"] - b["observed_cost"]
    if all(abs(a[k] - b[k]) < e["tie_hours"] for k in PHYS) and abs(dc) < e["tie_cost"]:
        return "tie"
    if dc <= -e["tie_cost"]:
        return "win"
    if dc >= e["tie_cost"]:
        return "loss"
    return "mixed"


def sensitivity_settings(cfg: dict) -> list[tuple[dict, dict]]:
    """(label, deep-copied config) for every weight x cost-level setting in eval.sensitivity."""
    s = cfg["eval"]["sensitivity"]
    out = []
    for wh, ws, wd, lv in itertools.product(s["w_heat"], s["w_smoke"], s["w_dual"], s["cost_levels"]):
        c = copy.deepcopy(cfg)
        c["weights"] = {"w_heat": wh, "w_smoke": ws, "w_dual": wd}
        c["heat"]["cost_levels"] = dict(zip(("below_shade", "shade_to_high", "high"), lv))
        c["smoke"]["cost_levels"] = dict(zip(("below_101", "from_101_to_150", "at_or_above_151"), lv))
        out.append(({"w_heat": wh, "w_smoke": ws, "w_dual": wd, "levels": list(lv)}, c))
    return out


def weight_sensitivity(inputs: list[dict], cfg: dict) -> list[dict]:
    """Re-plan the optimizer per setting; score weight-independent metrics vs B2 (fixed blocks).

    inputs: [{"id", "stratum", "provenance", "ft", "fa", "ot", "oa"}]. Returns one row per setting with
    per-day differences (optimizer - B2) in hours >=95F and AQI>=101 hours.
    """
    rows = []
    for label, c in sensitivity_settings(cfg):
        days = []
        for d in inputs:
            opt = exposure(d["ot"], d["oa"], optimize(d["ft"], d["fa"], cfg=c).blocks, cfg=cfg)
            ref = exposure(d["ot"], d["oa"], b2(d["ft"], d["fa"], cfg=c).blocks, cfg=cfg)
            days.append({"id": d["id"], "stratum": d["stratum"], "provenance": d["provenance"],
                         "d95": opt.hours_ge_95f - ref.hours_ge_95f,
                         "d101": opt.hours_aqi_ge_101 - ref.hours_aqi_ge_101})
        rows.append({"setting": label, "days": days})
    return rows


def forecast_sensitivity(days: list[DayRecord], pool: list[DayRecord], cfg: dict) -> dict[str, list[dict]]:
    """Optimizer vs B2 outcome per day under each proxy (prev-day only, 7-day mean only, default blend)."""
    proxies = {**cfg["eval"]["forecast_proxies"], "default_blend": {}}
    out = {}
    for name, override in proxies.items():
        c = copy.deepcopy(cfg)
        c["forecast"].update(override)
        rows = []
        for d in days:
            ft, fa = forecast_arrays(d, pool, c)
            ot, oa = day_arrays(d)
            a = score(optimize(ft, fa, cfg=cfg).blocks, ot, oa, cfg)
            b = score(b2(ft, fa, cfg=cfg).blocks, ot, oa, cfg)
            rows.append({"id": d.id, "stratum": stratum(ot, oa, cfg), "provenance": d.provenance,
                         "physical": classify_physical(a, b, cfg), "cost": classify(a, b, cfg)})
        out[name] = rows
    return out
