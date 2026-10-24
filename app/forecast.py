"""Leakage-safe forecast proxy for day D, plus an ORACLE upper bound.

FORECAST: per slot, w_prev * (D-1 profile) + w_mean * mean(D-1 .. D-k), with weights and k
from config.yaml `forecast`. Only pool days dated strictly before D are read; day D's values
(and any later day's) are never touched.
ORACLE: returns day D's observed truth, labeled "ORACLE". It is an upper bound, not a forecast.
"""
from datetime import date, timedelta
from typing import Literal

import numpy as np
from pydantic import BaseModel

from app.config import load_config
from app.models import DayRecord

FIELDS = ("temp_f", "rh", "solar_wm2", "pm25_ugm3")


class ForecastResult(BaseModel):
    method: Literal["FORECAST", "ORACLE"]
    target_id: str
    target_date: str
    source_dates: list[str]
    day: DayRecord


def _date(d: DayRecord) -> date:
    if d.date is None:
        raise ValueError(f"day {d.id} has no date; forecasting needs dated records")
    return date.fromisoformat(d.date)


def forecast(target: DayRecord, pool: list[DayRecord], oracle: bool = False,
             cfg: dict | None = None) -> ForecastResult:
    """Profile for `target` built from `pool`. Only target's id/label/region/date are used unless oracle."""
    d0 = _date(target)
    if oracle:
        day = target.model_copy(deep=True, update={"id": f"{target.id}#oracle",
                                                   "label": f"ORACLE: {target.label}"})
        return ForecastResult(method="ORACLE", target_id=target.id, target_date=target.date,
                              source_dates=[target.date], day=day)

    f = (cfg or load_config())["forecast"]
    earlier: dict[date, DayRecord] = {}
    for d in pool:
        dd = _date(d)
        if d.region != target.region or dd >= d0:  # strictly earlier only: no leakage
            continue
        if dd in earlier:
            raise ValueError(f"duplicate pool days for {dd} in region {d.region}")
        earlier[dd] = d

    need = [d0 - timedelta(days=i) for i in range(1, f["prior_days"] + 1)]
    missing = [x.isoformat() for x in need if x not in earlier]
    if missing:
        raise ValueError(f"forecast for {d0} needs prior days {missing}")
    prior = [earlier[x] for x in need]
    prev = prior[0]

    profiles = {}
    for k in FIELDS:
        mean = np.mean([getattr(p, k) for p in prior], axis=0)
        blend = f["weight_prev_day"] * np.asarray(getattr(prev, k)) + f["weight_prior_mean"] * mean
        profiles[k] = np.round(blend, 3).tolist()
    provenance = "real_cached" if all(p.provenance == "real_cached" for p in prior) else "synthetic"
    day = DayRecord(id=f"{target.id}#forecast", label=f"FORECAST: {target.label}", region=target.region,
                    provenance=provenance, date=target.date, **profiles)
    return ForecastResult(method="FORECAST", target_id=target.id, target_date=target.date,
                          source_dates=[x.isoformat() for x in need], day=day)
