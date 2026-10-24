"""Real-data job helpers with canned responses only (network calls fail the test)."""
from datetime import date

import numpy as np
import pytest

from app.config import load_config
from app.forecast import forecast
from data import real_checks as rc
from data import real_job

NAN = np.nan
JOB = load_config()["real_job"]


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    import requests

    def boom(*a, **k):
        raise AssertionError("network call in tests")
    monkeypatch.setattr(requests, "get", boom)


def _cimis(fields=("HlyAirTmp", "HlyRelHum", "HlySolRad"), units=("(C)", "(%)", "(W/sq.m)")):
    rec = {"Date": "2024-07-01", "Hour": "0100", **{f: {"Value": "30", "Unit": u} for f, u in zip(fields, units)}}
    return {"Data": {"Providers": [{"Records": [rec, {**rec, "Hour": "2400"}]}]}}


AIRNOW_OK = [{"UTC": "2024-07-01T07:00", "Parameter": "PM2.5", "Unit": "UG/M3", "Value": 12.0, "AQI": 50,
              "IntlAQSCode": "840060190011", "Latitude": 36.78, "Longitude": -119.77, "SiteName": "Fresno"}]
AIRNOW_AQI_ONLY = [{"UTC": "2024-07-01T07:00", "Parameter": "PM2.5", "AQI": 50, "IntlAQSCode": "840060190011",
                    "Latitude": 36.78, "Longitude": -119.77}]


def _status(checks, item_part):
    return [c["status"] for c in checks if item_part in c["item"]]


def test_cimis_schema_checks():
    cfg = load_config()
    good = rc.check_cimis(_cimis(), cfg["real_data"]["cimis"], JOB["cimis_expected_units"])
    assert all(c["status"] in ("confirmed", "unverifiable") for c in good)
    assert _status(good, "timezone") == ["unverifiable"]
    bad = rc.check_cimis(_cimis(fields=("HlyAirTmp", "HlyRelHum", "HlySolarX"), units=("(F)", "(%)", "(W)")),
                         cfg["real_data"]["cimis"], JOB["cimis_expected_units"])
    assert "differed" in _status(bad, "HlySolRad.Value") and "differed" in _status(bad, "unit of HlyAirTmp")
    assert rc.check_cimis({"oops": 1}, cfg["real_data"]["cimis"], {})[0]["status"] == "differed"


def test_airnow_schema_and_aqi_only_stops_preflight():
    cfg = load_config()
    assert rc.airnow_concentrations_available(AIRNOW_OK)
    ok, checks = rc.preflight(_cimis(), AIRNOW_OK, cfg)
    assert ok and _status(checks, "concentrations") == ["confirmed"]
    assert not rc.airnow_concentrations_available(AIRNOW_AQI_ONLY)
    ok, checks = rc.preflight(_cimis(), AIRNOW_AQI_ONLY, cfg)
    assert not ok and _status(checks, "concentrations") == ["differed"]
    md = rc.notes_markdown(checks, {}, "AirNow returned AQI only", [])
    assert "STOPPED" in md and "Differed" in md


def test_gap_filling_up_to_2_hours_only():
    two = np.array([1, 2, NAN, NAN, 5, 6], dtype=float)
    assert rc.fill_short_gaps(two, 2).tolist() == [1, 2, 3, 4, 5, 6]
    three = np.array([1, NAN, NAN, NAN, 5, 6], dtype=float)
    assert np.isnan(rc.fill_short_gaps(three, 2)[1:4]).all()
    edge = np.array([NAN, 2, 3], dtype=float)
    assert np.isnan(rc.fill_short_gaps(edge, 2)[0])  # edge gaps are not interpolated


def _day(temp_missing=(), pm_missing=()):
    t, p = np.linspace(70, 100, 24), np.linspace(5, 40, 24)
    t[list(temp_missing)] = NAN
    p[list(pm_missing)] = NAN
    return {"temp_f": t, "rh": np.full(24, 30.0), "solar_wm2": np.zeros(24), "pm25_ugm3": p}


@pytest.mark.parametrize("temp_missing, pm_missing, usable", [
    ((), (), True),
    ((10, 11), (), True),             # 2 h interior gap: filled -> 100%
    ((10, 11, 12), (), False),        # 3 h interior gap: not filled -> 87.5% < 90%
    ((), (0, 1), True),               # 2 h edge gap: 91.7% observed -> usable, edge held at nearest
    ((), (0, 1, 2), False),           # 3 h edge gap: 87.5%
    ((5, 6), (20, 21, 22), False),    # PM2.5 fails even though temp passes
])
def test_ninety_percent_rule(temp_missing, pm_missing, usable):
    filled, reasons, info = rc.assess_day(_day(temp_missing, pm_missing), JOB)
    assert (filled is not None) == usable
    if usable:
        assert all(not np.isnan(v).any() and len(v) == 24 for v in filled.values())
    else:
        assert reasons and "need 90%" in reasons[0]


def test_resume_uses_cache_and_skips_written_days(tmp_path, monkeypatch):
    f = real_job.Fetcher(tmp_path / "raw", JOB["throttle"], sleep=lambda s: None)
    (tmp_path / "raw" / "cimis").mkdir(parents=True)
    (tmp_path / "raw" / "cimis" / "80-2024-07-01.json").write_text('{"cached": true}', encoding="utf-8")
    assert f.get("https://example.invalid", {"appKey": "SECRET"}, "cimis/80-2024-07-01") == {"cached": True}
    assert f.network_calls == 0

    class R:
        status_code = 200
        def json(self):
            return {"fresh": 1}
    calls = []
    monkeypatch.setattr("requests.get", lambda *a, **k: calls.append(1) or R())
    assert f.get("https://example.invalid", {}, "airnow/x") == {"fresh": 1}
    assert f.get("https://example.invalid", {}, "airnow/x") == {"fresh": 1} and len(calls) == 1  # 2nd from cache

    days = [date(2024, 7, 1), date(2024, 7, 2)]
    (tmp_path / "real-2024-07-01-fresno.json").write_text("{}", encoding="utf-8")
    assert real_job.pending(days, "fresno", tmp_path) == [date(2024, 7, 2)]


def test_client_errors_not_retried_and_key_not_leaked(tmp_path, monkeypatch):
    class R:
        status_code = 401
    calls = []
    monkeypatch.setattr("requests.get", lambda *a, **k: calls.append(1) or R())
    f = real_job.Fetcher(tmp_path, JOB["throttle"], sleep=lambda s: None)
    with pytest.raises(real_job.FetchError) as e:
        f.get("https://example.invalid", {"API_KEY": "SECRET123"}, "airnow/y")
    assert len(calls) == 1 and "SECRET123" not in str(e.value)


def test_season_days_include_history_window():
    days = real_job.season_days(JOB)
    assert days[0] == date(2022, 5, 18) and date(2025, 9, 30) in days and date(2023, 10, 1) not in days
    assert len(days) == 4 * (14 + 122)


def test_forecast_requires_calendar_adjacent_days(history):
    target = history[-1]  # 2025-07-31: D-1..D-7 = 07-24..07-30
    assert forecast(target, history).method == "FORECAST"
    gap = [d for d in history if d.date != "2025-07-27"]  # still 12 earlier days, but D-4 missing
    with pytest.raises(ValueError, match="2025-07-27"):
        forecast(target, gap)
