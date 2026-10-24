"""Scenario-averaged ("robust") planner.

Scenarios for day D = proxy forecast for D + residuals (observed minus proxy forecast) of up to
`robust.max_residual_days` prior days. Each residual day's forecast is itself leakage-safe (uses only
days before it), and only days before D are used, so day D's data is never read. The per-slot expected
cost (scenario mean, same cost function) goes through the same search as app/optimizer.py.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np

from app.aqi import pm25_to_aqi
from app.config import load_config
from app.exposure import exposure, slot_cost
from app.forecast import forecast
from app.models import DayRecord, ShiftPlan
from app.optimizer import optimize, optimize_cost

FALLBACK_FLAG = "robust_fallback_insufficient_history"


@dataclass
class RobustResult:
    plan: ShiftPlan
    uncertainty: dict | None           # None on fallback
    flags: list[str] = field(default_factory=list)
    residual_dates: list[str] = field(default_factory=list)


def residuals(target: DayRecord, pool: list[DayRecord], cfg: dict) -> list[tuple[str, np.ndarray, np.ndarray]]:
    """(date, temp residual F, PM2.5 residual ug/m3) for prior days D-1..D-k that have their own forecast."""
    d0 = date.fromisoformat(target.date)
    lo = (d0 - timedelta(days=cfg["robust"]["max_residual_days"])).isoformat()
    prior = sorted((d for d in pool if d.region == target.region and d.date and lo <= d.date < target.date),
                   key=lambda d: d.date, reverse=True)
    out = []
    for p in prior:
        try:
            fc = forecast(p, pool, cfg=cfg)
        except ValueError:  # this prior day has no history of its own
            continue
        out.append((p.date, np.asarray(p.temp_f) - np.asarray(fc.day.temp_f),
                    np.asarray(p.pm25_ugm3) - np.asarray(fc.day.pm25_ugm3)))
    return out


def robust_plan(target: DayRecord, pool: list[DayRecord], cfg: dict | None = None,
                weights: dict | None = None, **shift_kw) -> RobustResult:
    """Robust plan for `target`. Raises ValueError (like forecast) if D itself has no proxy forecast."""
    c = cfg or load_config()
    base = forecast(target, pool, cfg=c)
    ft, fpm = np.asarray(base.day.temp_f, dtype=float), np.asarray(base.day.pm25_ugm3, dtype=float)
    res = residuals(target, pool, c)
    dates = [r[0] for r in res]
    if len(res) < c["robust"]["min_residual_days"]:
        plan = optimize(ft, pm25_to_aqi(fpm).aqi, weights=weights, cfg=c, name="robust", **shift_kw)
        return RobustResult(plan, None, [FALLBACK_FLAG], dates)

    temps = [ft + rt for _, rt, _ in res]
    aqis = [pm25_to_aqi(np.clip(fpm + rp, 0, None)).aqi for _, _, rp in res]
    expected = np.mean([slot_cost(t, a, weights, c) for t, a in zip(temps, aqis)], axis=0)
    plan = optimize_cost(expected, cfg=c, name="robust", **shift_kw)

    q = c["robust"]["uncertainty_percentile"]
    scen = [exposure(t, a, plan.blocks, cfg=c) for t, a in zip(temps, aqis)]

    def spread(k: str) -> dict:
        v = np.array([getattr(m, k) for m in scen])
        return {"mean": round(float(v.mean()), 4), f"p{q}": round(float(np.percentile(v, q)), 4)}

    unc = {"n_scenarios": len(res), "hours_ge_95f": spread("hours_ge_95f"),
           "hours_aqi_ge_101": spread("hours_aqi_ge_101")}
    return RobustResult(plan, unc, [], dates)
