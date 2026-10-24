"""fetch_real: no network. Missing keys exit 0; adapters parse canned payloads into a DayRecord."""
from datetime import date, datetime, timedelta, timezone

import numpy as np
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
    # Summer: local hour h (PDT) = PST hour-ending h, on PST date D (h >= 1) or D-1 HE 2400 (h = 0).
    recs = [{"Date": "2025-07-31", "Hour": "2400"}] + [{"Date": "2025-08-01", "Hour": f"{he:02d}00"}
                                                       for he in range(1, 25) if he != 6]  # local 06:00 missing
    for r in recs:
        r.update(HlyAirTmp={"Value": "30"}, HlyRelHum={"Value": "40"}, HlySolRad={"Value": "500"})
    cimis = {"Data": {"Providers": [{"Records": recs}]}}
    utc0 = datetime(2025, 8, 1, 7, tzinfo=timezone.utc)  # local midnight PDT
    airnow = [{"UTC": (utc0 + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M"), "Value": float(h)}
              for h in range(24)] + [{"UTC": utc0.strftime("%Y-%m-%dT%H:%M"), "Value": -999.0}]
    monkeypatch.setattr(fetch_real.CimisAdapter, "request", lambda self, d, k: cimis)
    monkeypatch.setattr(fetch_real.AirNowAdapter, "request", lambda self, d, k: airnow)
    rec = fetch_real.build_day(DAY, fetch_real.make_adapters(cfg), {"CIMIS_APPKEY": "k", "AIRNOW_KEY": "k"}, cfg)
    assert rec.provenance == "real_cached" and rec.date == "2025-08-01"
    assert rec.temp_f[0] == pytest.approx(86.0) and rec.temp_f[6 * 4] == pytest.approx(86.0)
    assert rec.pm25_ugm3[0] == 0.0 and rec.pm25_ugm3[13 * 4 + 3] == 13.0  # -999 sentinel ignored


def test_too_many_missing_hours_raises():
    with pytest.raises(ValueError, match="missing"):
        fetch_real.hourly_to_slots(np.full(24, np.nan), 4, "temp_f")


def test_naive_timestamps_rejected():
    with pytest.raises(ValueError, match="aware"):
        fetch_real.to_local_hourly([(datetime(2025, 8, 1, 3), 1.0)], DAY, fetch_real.ZoneInfo("America/Los_Angeles"))
