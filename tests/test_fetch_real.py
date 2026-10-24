"""fetch_real: no network. Missing keys exit 0; adapters parse canned payloads into a DayRecord."""
from datetime import date, datetime, timedelta

import pytest

from app.config import load_config
from data import fetch_real

DAY = date(2025, 8, 1)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    import requests

    def boom(*a, **k):
        raise AssertionError("network call in tests")
    monkeypatch.setattr(requests, "get", boom)


def test_missing_keys_print_message_and_exit_0(monkeypatch, capsys):
    monkeypatch.delenv("CIMIS_APPKEY", raising=False)
    monkeypatch.setenv("AIRNOW_KEY", "x")
    assert fetch_real.main(["2025-08-01"]) == 0
    out = capsys.readouterr().out
    assert "CIMIS_APPKEY" in out and "AIRNOW_KEY" not in out


def test_adapters_build_real_cached_day(monkeypatch):
    cfg = load_config()["real_data"]
    cimis = {"Data": {"Providers": [{"Records": [
        {"Hour": f"{h + 1:02d}00", "HlyAirTmp": {"Value": "30"}, "HlyRelHum": {"Value": "40"},
         "HlySolRad": {"Value": "500"}} for h in range(24) if h != 5]}]}}  # hour 5 missing -> interpolated
    utc0 = datetime(2025, 8, 1) - timedelta(hours=cfg["airnow"]["utc_offset_hours"])
    airnow = [{"UTC": (utc0 + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M"), "Value": float(h)}
              for h in range(24)] + [{"UTC": utc0.strftime("%Y-%m-%dT%H:%M"), "Value": -999.0}]
    monkeypatch.setattr(fetch_real.CimisAdapter, "request", lambda self, d, k: cimis)
    monkeypatch.setattr(fetch_real.AirNowAdapter, "request", lambda self, d, k: airnow)
    rec = fetch_real.build_day(DAY, fetch_real.make_adapters(cfg), {"CIMIS_APPKEY": "k", "AIRNOW_KEY": "k"}, cfg)
    assert rec.provenance == "real_cached" and rec.date == "2025-08-01"
    assert rec.temp_f[0] == pytest.approx(86.0) and rec.temp_f[5 * 4] == pytest.approx(86.0)
    assert rec.pm25_ugm3[0] == 0.0 and rec.pm25_ugm3[13 * 4 + 3] == 13.0  # -999 sentinel ignored


def test_too_many_missing_hours_raises():
    import numpy as np
    with pytest.raises(ValueError, match="missing"):
        fetch_real.hourly_to_slots(np.full(24, np.nan), 4, "temp_f")
