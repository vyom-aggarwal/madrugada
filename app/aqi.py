"""PM2.5 (ug/m3) -> US AQI using the breakpoint table in config.yaml (aqi_pm25.breakpoints).

EPA practice: truncate concentration to 0.1 ug/m3, linear-interpolate within the matching
breakpoint row, round AQI to the nearest integer. Concentrations above the top row are
extrapolated along the top row's slope and flagged; they are never clipped.
"""
from dataclasses import dataclass

import numpy as np

from app.config import load_config


@dataclass
class AqiResult:
    aqi: np.ndarray           # int AQI per input value
    extrapolated: np.ndarray  # bool: concentration above the top breakpoint

    @property
    def any_extrapolated(self) -> bool:
        return bool(self.extrapolated.any())


def load_breakpoints(cfg: dict | None = None) -> np.ndarray:
    """Return breakpoints as an (n, 4) float array [pm_low, pm_high, aqi_low, aqi_high]."""
    rows = np.asarray((cfg or load_config())["aqi_pm25"]["breakpoints"], dtype=float)
    if rows.ndim != 2 or rows.shape[1] != 4:
        raise ValueError("aqi_pm25.breakpoints must be rows of [pm_low, pm_high, aqi_low, aqi_high]")
    if np.any(np.diff(rows[:, 0]) <= 0):
        raise ValueError("aqi_pm25.breakpoints must be sorted by pm_low")
    return rows


def truncate_pm25(pm) -> np.ndarray:
    """Truncate to one decimal (EPA). Rounding to 1e-6 first avoids float artifacts (2.3 -> 2.2)."""
    pm = np.asarray(pm, dtype=float)
    return np.floor(np.round(pm * 10, 6)) / 10


def pm25_to_aqi(pm, breakpoints: np.ndarray | None = None) -> AqiResult:
    """Vectorized PM2.5 -> AQI. Negative concentrations (sensor noise) are treated as 0."""
    bp = load_breakpoints() if breakpoints is None else np.asarray(breakpoints, dtype=float)
    c = np.maximum(truncate_pm25(pm), 0.0)
    idx = np.clip(np.searchsorted(bp[:, 0], c, side="right") - 1, 0, len(bp) - 1)
    c_lo, c_hi, i_lo, i_hi = (bp[idx, k] for k in range(4))
    aqi = (i_hi - i_lo) / (c_hi - c_lo) * (c - c_lo) + i_lo
    aqi = np.floor(aqi + 0.5).astype(int)  # round half up
    return AqiResult(aqi=aqi, extrapolated=c > bp[-1, 1])


def pm25_to_aqi_scalar(pm: float, breakpoints: np.ndarray | None = None) -> tuple[int, bool]:
    r = pm25_to_aqi([pm], breakpoints)
    return int(r.aqi[0]), bool(r.extrapolated[0])


def extrapolation_warning(result: AqiResult) -> str | None:
    if not result.any_extrapolated:
        return None
    n = int(result.extrapolated.sum())
    return (f"{n} slot(s) have PM2.5 above the top AQI breakpoint; "
            "AQI was extrapolated beyond the EPA table and is approximate.")
