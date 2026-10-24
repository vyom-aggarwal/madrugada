"""Synthetic fixtures: schema, provenance, dates, determinism, and scenario shapes."""
import numpy as np
import pytest

from app.aqi import pm25_to_aqi
from app.config import load_config
from app.models import DayRecord
from data import make_fixtures
from tests.conftest import load_raw

ALL_FILES = ("days.json", "history.json")
NAMES = ["heat_only", "smoke_only", "co_occurring", "early_pm25_peak", "mild", "co_occurring_offset"]


@pytest.mark.parametrize("fname", ALL_FILES)
def test_every_fixture_is_a_synthetic_day_record(fname):
    raw = load_raw(fname)
    assert raw
    for d in raw:
        rec = DayRecord(**d)
        assert rec.provenance == "synthetic"
        assert rec.label.startswith("SYNTHETIC")


def test_counts_names_and_history_is_earlier(test_days, history):
    assert [d.id.split("-", 4)[-1] for d in test_days] == NAMES
    assert len(history) == 14
    assert max(h.date for h in history) < min(d.date for d in test_days)


def test_fixtures_are_reproducible():
    days, hist = make_fixtures.build()
    assert days == load_raw("days.json") and hist == load_raw("history.json")


def _hazards(d: DayRecord):
    cfg = load_config()
    t = np.array(d.temp_f)
    aqi = pm25_to_aqi(d.pm25_ugm3).aqi
    dual = (t >= cfg["dual_hazard"]["temp_f"]) & (aqi >= cfg["dual_hazard"]["aqi"])
    return t, aqi, dual, cfg


def test_scenario_shapes(test_days):
    by = dict(zip(NAMES, test_days))
    t, aqi, _, cfg = _hazards(by["heat_only"])
    assert t.max() >= cfg["heat"]["high_heat_f"] and aqi.max() < cfg["smoke"]["aqi_unhealthy_sensitive"]
    t, aqi, _, cfg = _hazards(by["smoke_only"])
    assert t.max() < cfg["dual_hazard"]["temp_f"] and aqi.max() >= cfg["smoke"]["aqi_wildfire_rule"]
    _, _, dual, _ = _hazards(by["co_occurring"])
    assert dual.any()
    pm = np.array(by["early_pm25_peak"].pm25_ugm3)
    assert pm.argmax() < 24 and pm[48] < pm.max() / 3  # peak before 06:00, low at noon
    t, aqi, _, cfg = _hazards(by["mild"])
    assert t.max() < cfg["heat"]["shade_trigger_f"] and aqi.max() < cfg["smoke"]["aqi_unhealthy_sensitive"]
    d = by["co_occurring_offset"]
    t, aqi, _, cfg = _hazards(d)
    assert np.argmax(d.temp_f) >= 64 and np.argmax(d.pm25_ugm3) < 32  # heat after 16:00, smoke before 08:00
    assert t.max() >= cfg["heat"]["high_heat_f"] and aqi.max() >= cfg["smoke"]["aqi_wildfire_rule"]
