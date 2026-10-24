"""Generate SYNTHETIC fixture days (provenance="synthetic") with a fixed random seed.

Writes data/fixtures/days.json (6 scenario days, 2025-08-01..06) and
data/fixtures/history.json (14 earlier days, 2025-07-18..31). These are NOT measurements.
Run: python data/make_fixtures.py
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.models import SLOTS_PER_DAY, DayRecord  # noqa: E402

SEED = 20250801
OUT_DIR = ROOT / "data" / "fixtures"
REGION = "fresno"
FIRST_TEST_DATE = date(2025, 8, 1)
HISTORY_DAYS = 14
HOURS = np.arange(SLOTS_PER_DAY) / (SLOTS_PER_DAY / 24)  # slot start, local hours
SUNRISE, SUNSET, SOLAR_PEAK = 6.25, 20.0, 950.0

# name, label, temp (tmin, tmax, peak_hour), rh (max, min), pm (base, event, center_h, width_h), solar dimming
SCENARIOS = [
    ("heat_only", "SYNTHETIC: hot afternoon, clean air",
     (72, 105, 15.5), (55, 12), (5, 0, 12.0, 1.0), 0.0),
    ("smoke_only", "SYNTHETIC: moderate temps, smoke event",
     (60, 82, 15.0), (75, 35), (25, 110, 13.0, 3.5), 0.3),
    ("co_occurring", "SYNTHETIC: hot afternoon with smoke",
     (70, 102, 15.5), (55, 15), (30, 90, 15.0, 4.0), 0.25),
    ("early_pm25_peak", "SYNTHETIC: pre-dawn PM2.5 peak, clearing by day",
     (64, 90, 15.5), (80, 25), (10, 85, 4.0, 2.0), 0.1),
    ("mild", "SYNTHETIC: mild temps, clean air",
     (55, 76, 15.0), (80, 40), (5, 0, 12.0, 1.0), 0.0),
    ("co_occurring_offset", "SYNTHETIC: late-afternoon heat, early-morning smoke",
     (70, 103, 17.5), (55, 14), (20, 110, 5.0, 2.0), 0.15),
]


def _noise(rng, sd):
    """Smooth noise: white noise averaged over a 2-hour window."""
    return np.convolve(rng.normal(0, sd, SLOTS_PER_DAY), np.ones(8) / 8, mode="same")


def _bump(center, width):
    return np.exp(-0.5 * ((HOURS - center) / width) ** 2)


def profiles(temp, rh, pm, dim, rng) -> dict:
    tmin, tmax, peak = temp
    shape = 0.5 * (1 + np.cos(2 * np.pi * (HOURS - peak) / 24))
    t = tmin + (tmax - tmin) * shape + _noise(rng, 2.0)
    h = rh[0] - (rh[0] - rh[1]) * shape + _noise(rng, 3.0)
    daylight = (HOURS > SUNRISE) & (HOURS < SUNSET)
    s = np.where(daylight, SOLAR_PEAK * np.sin(np.pi * (HOURS - SUNRISE) / (SUNSET - SUNRISE)), 0.0)
    base, event, center, width = pm
    p = base + event * _bump(center, width) + _noise(rng, 3.0)
    return {"temp_f": t, "rh": np.clip(h, 5, 100), "solar_wm2": np.clip(s * (1 - dim), 0, None),
            "pm25_ugm3": np.clip(p, 0, None)}


def _record(name, label, d, prof) -> dict:
    rec = DayRecord(id=f"syn-{d.isoformat()}-{name}", label=label, region=REGION,
                    provenance="synthetic", date=d.isoformat(),
                    **{k: np.round(v, 2).tolist() for k, v in prof.items()})
    return rec.model_dump()


def build() -> tuple[list[dict], list[dict]]:
    """Return (test_days, history). Deterministic for a given SEED."""
    rng = np.random.default_rng(SEED)
    history = []
    for i in range(HISTORY_DAYS, 0, -1):
        d = FIRST_TEST_DATE - timedelta(days=i)
        tmax = rng.uniform(88, 102)
        temp = (tmax - rng.uniform(26, 32), tmax, rng.uniform(15.0, 16.5))
        smoky = rng.random() < 0.25
        pm = (rng.uniform(5, 18), rng.uniform(30, 80) if smoky else 0.0,
              rng.uniform(3, 16), rng.uniform(2, 4))
        history.append(_record("history", "SYNTHETIC: history day", d,
                               profiles(temp, (70, 15), pm, 0.0, rng)))
    days = [_record(name, label, FIRST_TEST_DATE + timedelta(days=i), profiles(temp, rh, pm, dim, rng))
            for i, (name, label, temp, rh, pm, dim) in enumerate(SCENARIOS)]
    return days, history


def _write(path: Path, records: list[dict]) -> None:
    path.write_text("[\n" + ",\n".join(json.dumps(r) for r in records) + "\n]\n", encoding="utf-8")


def main() -> None:
    days, history = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _write(OUT_DIR / "days.json", days)
    _write(OUT_DIR / "history.json", history)
    print(f"wrote {len(days)} SYNTHETIC test days and {len(history)} SYNTHETIC history days to {OUT_DIR}")


if __name__ == "__main__":
    main()
