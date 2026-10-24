"""Per-slot hazard flags, weighted slot cost, and exposure-hours for a set of work slots.

Everything takes plain arrays (temp_f, AQI) so plans can be built on forecast arrays and scored
on observed arrays. Thresholds, cost levels and weights come from config.yaml.
"""
import numpy as np

from app.aqi import pm25_to_aqi
from app.config import load_config
from app.models import Block, DayRecord, ExposureMetrics


def slot_hours(cfg: dict | None = None) -> float:
    return (cfg or load_config())["grid"]["slot_minutes"] / 60


def hhmm_to_slot(hhmm: str, cfg: dict | None = None) -> int:
    step = (cfg or load_config())["grid"]["slot_minutes"]
    h, m = map(int, hhmm.split(":"))
    if (h * 60 + m) % step:
        raise ValueError(f"{hhmm} is not on the {step}-minute grid")
    return (h * 60 + m) // step


def slot_to_hhmm(slot: int, cfg: dict | None = None) -> str:
    minutes = slot * (cfg or load_config())["grid"]["slot_minutes"]
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def day_arrays(day: DayRecord) -> tuple[np.ndarray, np.ndarray]:
    """(temp_f, AQI) arrays for a day; AQI from app.aqi."""
    return np.asarray(day.temp_f, dtype=float), pm25_to_aqi(day.pm25_ugm3).aqi


def hazard_flags(temp_f, aqi, cfg: dict | None = None) -> dict[str, np.ndarray]:
    c = cfg or load_config()
    t, a = np.asarray(temp_f, dtype=float), np.asarray(aqi, dtype=float)
    return {
        "ge_95f": t >= c["heat"]["high_heat_f"],
        "ge_80f": t >= c["heat"]["shade_trigger_f"],
        "aqi_ge_101": a >= c["smoke"]["aqi_unhealthy_sensitive"],
        "aqi_ge_151": a >= c["smoke"]["aqi_wildfire_rule"],
        "dual": (t >= c["dual_hazard"]["temp_f"]) & (a >= c["dual_hazard"]["aqi"]),
    }


def slot_cost(temp_f, aqi, weights: dict | None = None, cfg: dict | None = None) -> np.ndarray:
    """w_heat*heat_cost + w_smoke*smoke_cost + w_dual*dual_flag per slot. `weights` overrides config."""
    c = cfg or load_config()
    w = {**c["weights"], **(weights or {})}
    f = hazard_flags(temp_f, aqi, c)
    hl, sl = c["heat"]["cost_levels"], c["smoke"]["cost_levels"]
    heat = np.where(f["ge_95f"], hl["high"], np.where(f["ge_80f"], hl["shade_to_high"], hl["below_shade"]))
    smoke = np.where(f["aqi_ge_151"], sl["at_or_above_151"],
                     np.where(f["aqi_ge_101"], sl["from_101_to_150"], sl["below_101"]))
    return w["w_heat"] * heat + w["w_smoke"] * smoke + w["w_dual"] * f["dual"]


def blocks_to_mask(blocks: list[Block], n_slots: int) -> np.ndarray:
    mask = np.zeros(n_slots, dtype=bool)
    for b in blocks:
        mask[b.start_slot:b.end_slot] = True
    return mask


def plan_cost(blocks: list[Block], temp_f, aqi, weights: dict | None = None, cfg: dict | None = None) -> float:
    return float(slot_cost(temp_f, aqi, weights, cfg)[blocks_to_mask(blocks, len(temp_f))].sum())


def exposure(temp_f, aqi, work, paid_target_hours: float | None = None,
             cfg: dict | None = None) -> ExposureMetrics:
    """Exposure-hours over worked slots. `work` is a bool mask or a list of Blocks."""
    c = cfg or load_config()
    mask = work.astype(bool) if isinstance(work, np.ndarray) else blocks_to_mask(work, len(temp_f))
    h = slot_hours(c)
    f = hazard_flags(temp_f, aqi, c)

    def hours(k: str) -> float:
        return float(f[k][mask].sum() * h)

    paid = float(mask.sum() * h)
    return ExposureMetrics(
        hours_ge_95f=hours("ge_95f"), hours_ge_80f=hours("ge_80f"),
        hours_aqi_ge_101=hours("aqi_ge_101"), hours_aqi_ge_151=hours("aqi_ge_151"),
        dual_hazard_hours=hours("dual"), paid_hours=paid,
        paid_hours_retained_pct=100.0 * paid / paid_target_hours if paid_target_hours else 100.0,
    )
