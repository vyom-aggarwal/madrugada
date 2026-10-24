"""'Hours scheduling can't fix' readout: validation, a hand-built day, the crew-sheet line, UI wiring."""
import re
from datetime import date, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app import main, planning, unfixable
from app.exposure import hhmm_to_slot
from app.models import DayRecord

client = TestClient(main.app)
ROOT = Path(__file__).resolve().parent.parent


def _hot_days(n=8):
    """Identical days: 100F from 12:00 to 18:00, 70F otherwise; clean air. The forecast equals the observed."""
    temp = [100.0 if 48 <= i < 72 else 70.0 for i in range(96)]
    return [DayRecord(id=f"hand-{i}", label="hand-built", region="fresno", provenance="synthetic",
                      date=(date(2024, 7, 1) + timedelta(days=i)).isoformat(), temp_f=temp, rh=[30.0] * 96,
                      solar_wm2=[0.0] * 96, pm25_ugm3=[5.0] * 96) for i in range(n)]


def _patch(monkeypatch, days):
    monkeypatch.setattr(planning, "load_days", lambda: tuple(days))
    unfixable.for_day.cache_clear()


def test_unknown_day_404_without_echo():
    hostile = "<script>nope</script>"
    r = client.get("/api/unfixable", params={"day_id": hostile})
    assert r.status_code == 404 and "Day not found" in r.json()["detail"] and "script" not in r.text


def test_hand_built_day(monkeypatch):
    days = _hot_days()
    _patch(monkeypatch, days)
    try:
        r = client.get("/api/unfixable", params={"day_id": "hand-7"})
        assert r.status_code == 200
        b = r.json()
        start, _ = unfixable.first_light(days[7])
        assert b["first_light_start"] == start and b["blocks"][0]["start"] == start
        # Independent brute force: 34 slots (8.5 h) in [first light, 19:00), blocks >= 8 slots, gap >= 4 slots;
        # hot slots are 48..71. The best layout minimizes hot slots (cost here is heat-only, clean air).
        s0, hot = hhmm_to_slot(start), set(range(48, 72))
        h = lambda a, b: len(hot.intersection(range(a, b)))  # noqa: E731
        best = min([h(s, s + 34) for s in range(s0, 76 - 34 + 1)] +
                   [h(s1, s1 + a) + h(s2, s2 + 34 - a) for a in range(8, 34 - 8 + 1)
                    for s1 in range(s0, 76) for s2 in range(s1 + a + 4, 76 - (34 - a) + 1)])
        expected = best / 4
        assert b["hours_ge_95f"] == {"planned": expected, "observed": expected} and expected > 0
        assert b["line"] == "These hours need shade, rest or crew changes, not a different start time."
        r = client.get("/api/unfixable", params={"day_id": "hand-7", "paid_hours": 12, "latest": "16:00"})
        assert r.status_code == 422 and "cannot hold" in r.json()["detail"]  # first light to 16:00 < 12 h
        assert client.get("/api/unfixable", params={"day_id": "hand-7", "paid_hours": 1}).status_code == 422
        sheet = client.get("/crew-sheet", params={"day_id": "hand-7"}).text
        assert "not a different start time" in sheet and "no otra hora de inicio" in sheet
        assert "forecast-based estimate" in sheet
    finally:
        unfixable.for_day.cache_clear()


def test_ui_wires_readout_and_story():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert "Hours scheduling can't fix" in html and "/api/unfixable" in html and "s.unfixable" in html
    assert "We tested whether shifting hours reduces heat exposure." in html
    ids = set(re.findall(r'id="([\w-]+)"', html))
    assert {"unfix-text", "unfix-note", "headline-detail"} <= ids
