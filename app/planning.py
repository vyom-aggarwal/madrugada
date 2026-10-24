"""Plan service behind the API: day store, cached plan computation, JSON-ready results.

Plans are built on the forecast arrays (proxy, or ORACLE truth) and scored twice: `planned` on
the forecast and `observed` on the day's actual values.
"""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.aqi import extrapolation_warning, invalid_input_warning, pm25_to_aqi
from app.baselines import b1, b2, b3_early, b3_late
from app.config import load_config
from app.exposure import exposure, hhmm_to_slot, plan_cost, slot_to_hhmm
from app.forecast import forecast
from app.models import DayRecord
from app.optimizer import optimize, pareto
from app.robust import robust_plan

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "data" / "fixtures"
CACHE = ROOT / "data" / "cache"
PLAN_NAMES = ("optimizer", "robust", "B1", "B2", "b3_early", "b3_late")


class UnknownDay(KeyError):
    pass


class NoHistory(ValueError):
    pass


def _read_list(path: Path) -> list[DayRecord]:
    return [DayRecord(**d) for d in json.loads(path.read_text(encoding="utf-8"))] if path.exists() else []


@lru_cache(maxsize=1)
def load_days() -> tuple[DayRecord, ...]:
    """Fixture test days, then cached real days, then fixture history days."""
    real = [DayRecord(**json.loads(p.read_text(encoding="utf-8"))) for p in sorted(CACHE.glob("*.json"))]
    return tuple(_read_list(FIXTURES / "days.json") + real + _read_list(FIXTURES / "history.json"))


def get_day(day_id: str) -> DayRecord:
    for d in load_days():
        if d.id == day_id:
            return d
    raise UnknownDay(day_id)


def day_summary(d: DayRecord) -> dict:
    return {"id": d.id, "label": d.label, "date": d.date, "provenance": d.provenance}


def blocks_json(blocks) -> list[dict]:
    return [{"start": slot_to_hhmm(b.start_slot), "end": slot_to_hhmm(b.end_slot),
             "start_slot": b.start_slot, "end_slot": b.end_slot} for b in blocks]


def thresholds(cfg: dict) -> dict:
    return {"heat_shade_f": cfg["heat"]["shade_trigger_f"], "heat_high_f": cfg["heat"]["high_heat_f"],
            "aqi_sensitive": cfg["smoke"]["aqi_unhealthy_sensitive"], "aqi_smoke_rule": cfg["smoke"]["aqi_wildfire_rule"],
            "dual_temp_f": cfg["dual_hazard"]["temp_f"], "dual_aqi": cfg["dual_hazard"]["aqi"]}


def _warnings(target, fc_day, fc_aqi, obs_aqi, oracle, earliest, latest, cfg) -> list[str]:
    out = []
    if target.provenance == "synthetic":
        out.append("SYNTHETIC data: illustration only, not a measurement.")
    if oracle:
        out.append("ORACLE mode: planned on the day's actual data (upper bound, not a forecast).")
    limit = cfg["purpleair"]["warn_above_ugm3"]
    for label, rec, res in (("forecast", fc_day, fc_aqi), ("observed", target, obs_aqi)):
        out += [f"{label}: {w}" for w in (extrapolation_warning(res), invalid_input_warning(res)) if w]
        arrays = [np.asarray(getattr(rec, k), dtype=float) for k in ("temp_f", "rh", "solar_wm2", "pm25_ugm3")]
        if any(not np.isfinite(a).all() for a in arrays):
            out.append(f"{label}: missing (non-finite) values in the data.")
        n = int((arrays[3] > limit).sum())
        if n:
            out.append(f"{label}: {n} slot(s) above {limit} ug/m3; if PurpleAir-derived, the EPA correction "
                       "underestimates at these levels.")
    e, l = hhmm_to_slot(earliest, cfg), hhmm_to_slot(latest, cfg)
    for name in ("B1", "B2"):
        b = cfg["baselines"][name]
        if hhmm_to_slot(b["start"], cfg) < e or hhmm_to_slot(b["end"], cfg) > l:
            out.append(f"{name} ({b['start']}-{b['end']}) lies outside the requested window; shown for comparison.")
    return out


@lru_cache(maxsize=512)
def plan_for(day_id: str, paid_hours: float, earliest: str, latest: str, oracle: bool) -> dict:
    """Full plan response for one (day, params). Cached: repeated slider positions are instant."""
    cfg = load_config()
    target = get_day(day_id)
    try:
        fc = forecast(target, list(load_days()), oracle=oracle)
    except ValueError as e:
        raise NoHistory(str(e)) from e
    ft, fa_res = np.asarray(fc.day.temp_f, dtype=float), pm25_to_aqi(fc.day.pm25_ugm3)
    ot, oa_res = np.asarray(target.temp_f, dtype=float), pm25_to_aqi(target.pm25_ugm3)
    fa, oa = fa_res.aqi, oa_res.aqi
    kw = {"paid_hours_target": paid_hours, "earliest_start": earliest, "latest_end": latest}
    rob = robust_plan(target, list(load_days()), **kw)  # always proxy + residual scenarios, even in ORACLE mode
    plans = {"optimizer": optimize(ft, fa, **kw), "robust": rob.plan, "B1": b1(ft, fa), "B2": b2(ft, fa),
             "b3_early": b3_early(ft, fa, **kw), "b3_late": b3_late(ft, fa, **kw)}
    plans_out, metrics = {}, {}
    for name, p in plans.items():
        obs = exposure(ot, oa, p.blocks, paid_hours, cfg)
        plans_out[name] = {"blocks": blocks_json(p.blocks), "paid_hours": obs.paid_hours,
                           "planned_cost": round(p.cost, 6), "observed_cost": round(plan_cost(p.blocks, ot, oa), 6)}
        metrics[name] = {"planned": exposure(ft, fa, p.blocks, paid_hours, cfg).model_dump(),
                         "observed": obs.model_dump()}
    plans_out["robust"].update(uncertainty=rob.uncertainty, flags=rob.flags, residual_dates=rob.residual_dates)
    warnings = _warnings(target, fc.day, fa_res, oa_res, oracle, earliest, latest, cfg) + rob.flags
    if oracle:
        warnings.append("robust plan uses the proxy forecast plus residual scenarios, not the day's actual data.")
    pts = [{"paid_fraction": q.paid_fraction, "heat_smoke_ratio": q.heat_smoke_ratio, "heat_hours": q.heat_hours,
            "smoke_hours": q.smoke_hours, "paid_hours": q.paid_hours, "blocks": blocks_json(q.plan.blocks)}
           for q in pareto(ft, fa, paid_hours_target=paid_hours, earliest_start=earliest, latest_end=latest)]
    return {
        "day": day_summary(target),
        "mode": "ORACLE" if oracle else "proxy",
        "request": {"paid_hours": paid_hours, "earliest": earliest, "latest": latest, "oracle": oracle},
        "forecast": {"temp_f": fc.day.temp_f, "aqi": fa.tolist(), "source_dates": fc.source_dates},
        "plan": plans_out["optimizer"],
        "plans": plans_out,
        "metrics": metrics,
        "pareto": pts,
        "thresholds": thresholds(cfg),
        "warnings": warnings,
    }
