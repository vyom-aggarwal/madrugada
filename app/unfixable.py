"""'Hours scheduling can't fix': hours at or above the high-heat trigger that remain in the best plan that starts
no earlier than first light (approximate sunrise minus 30 minutes). Non-logic, computed per request.

Reuses the frozen optimizer, forecast proxy and exposure functions read-only, and the approximate, unverified
NOAA sunrise function from analysis/sensitivity_start.py. Paid hours and latest end come from the request.
"""
from datetime import date
from functools import lru_cache
from pathlib import Path

import numpy as np

from analysis.sensitivity_start import coords, sunrise_local, sunrise_start
from app.aqi import pm25_to_aqi
from app.config import load_config
from app.exposure import day_arrays, exposure, slot_to_hhmm
from app.forecast import forecast
from app.models import DayRecord
from app.optimizer import optimize

MANIFEST = Path(__file__).resolve().parent.parent / "data" / "cache" / "meta" / "manifest.json"
LINE_EN = "These hours need shade, rest or crew changes, not a different start time."
LINE_ES = "Estas horas requieren sombra, descanso o cambios en la cuadrilla, no otra hora de inicio."


class WindowTooShort(ValueError):
    pass


def first_light(day: DayRecord) -> tuple[str, str]:
    """(first-light start 'HH:MM' on the grid, approximate sunrise 'HH:MM') for the day's date and station."""
    lat, lon, _ = coords(MANIFEST).get(day.region, (36.74, -119.79, "fallback"))
    d = date.fromisoformat(day.date)
    return sunrise_start(d, lat, lon, load_config()), sunrise_local(d, lat, lon).strftime("%H:%M")


def compute(target: DayRecord, pool: list[DayRecord], paid_hours: float, latest: str) -> dict:
    """Raises ValueError (no forecast history) or WindowTooShort (first light to latest cannot hold the hours)."""
    fc = forecast(target, pool)  # leakage-safe proxy, as /api/plan uses
    ft, fa = np.asarray(fc.day.temp_f, dtype=float), pm25_to_aqi(fc.day.pm25_ugm3).aqi
    ot, oa = day_arrays(target)
    start, sunrise = first_light(target)
    try:
        plan = optimize(ft, fa, paid_hours_target=paid_hours, earliest_start=start, latest_end=latest)
    except ValueError as e:
        raise WindowTooShort(f"first light ({start}) to latest end ({latest}) cannot hold {paid_hours:g} paid hours") from e
    planned, observed = exposure(ft, fa, plan.blocks), exposure(ot, oa, plan.blocks)
    return {"first_light_start": start, "sunrise_approx": sunrise,
            "blocks": [{"start": slot_to_hhmm(b.start_slot), "end": slot_to_hhmm(b.end_slot),
                        "start_slot": b.start_slot, "end_slot": b.end_slot} for b in plan.blocks],
            "paid_hours": planned.paid_hours,
            "hours_ge_95f": {"planned": planned.hours_ge_95f, "observed": observed.hours_ge_95f},
            "hours_aqi_ge_101": {"planned": planned.hours_aqi_ge_101, "observed": observed.hours_aqi_ge_101},
            "label": "forecast-based estimate (planned); observed = what happened on this replayed day",
            "line": LINE_EN, "line_es": LINE_ES,
            "note": "First light = approximate sunrise minus 30 minutes (NOAA equations, unverified), rounded to 15 minutes."}


@lru_cache(maxsize=512)
def for_day(day_id: str, paid_hours: float, latest: str) -> dict:
    from app.planning import get_day, pool_for
    target = get_day(day_id)
    return compute(target, pool_for(target), paid_hours, latest)
