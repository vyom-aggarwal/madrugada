"""Phase 0 smoke tests: app wiring, config completeness, model validation."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import load_config
from app.main import app
from app.models import SLOTS_PER_DAY, DayRecord

client = TestClient(app)


def test_health_and_static_mount():
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}
    r = client.get("/static/")
    assert r.status_code == 200 and "Madrugada" in r.text


def test_config_has_required_thresholds():
    cfg = load_config()
    assert cfg["grid"]["slots_per_day"] == SLOTS_PER_DAY
    assert (cfg["heat"]["shade_trigger_f"], cfg["heat"]["high_heat_f"]) == (80, 95)
    assert (cfg["smoke"]["aqi_unhealthy_sensitive"], cfg["smoke"]["aqi_wildfire_rule"]) == (101, 151)
    assert cfg["dual_hazard"] == {"temp_f": 90, "aqi": 101}
    assert {"w_heat", "w_smoke", "w_dual"} <= set(cfg["weights"])
    bps = cfg["aqi_pm25"]["breakpoints"]
    assert cfg["aqi_pm25"]["status"] == "unverified"
    assert all(len(row) == 4 for row in bps)
    assert [r[2] for r in bps] == sorted(r[2] for r in bps)


def _day(n: int) -> dict:
    return dict(id="d1", label="test", region="fresno", provenance="synthetic",
                temp_f=[70.0] * n, rh=[30.0] * n, solar_wm2=[0.0] * n, pm25_ugm3=[5.0] * n)


def test_day_record_validates_slot_count_and_provenance():
    DayRecord(**_day(SLOTS_PER_DAY))
    with pytest.raises(ValidationError):
        DayRecord(**_day(95))
    with pytest.raises(ValidationError):
        DayRecord(**{**_day(SLOTS_PER_DAY), "provenance": "measured"})
