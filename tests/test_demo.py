"""Demo hardening: clear 404, snapshot builder, rule-selected default day, UI banners."""
import json

from fastapi.testclient import TestClient

from app import main, planning, snapshot
from app.main import STATIC_DIR, app

client = TestClient(app)


def test_missing_day_404_has_clear_message():
    r = client.post("/api/plan", json={"day_id": "real-2099-01-01-nowhere"})
    assert r.status_code == 404
    assert "Day not found" in r.json()["detail"] and "/api/days" in r.json()["detail"]


def test_snapshot_builder(tmp_path):
    snap = snapshot.build()
    assert {"days", "eval", "plans", "default_params"} <= set(snap)
    ids = [d["id"] for d in snap["days"]]
    assert set(snap["plans"]) == set(ids)
    ok = {i: p for i, p in snap["plans"].items() if "error" not in p}
    assert len(ok) == 13 and all(p["mode"] == "proxy" and "robust" in p["plans"] for p in ok.values())
    assert all(p["status"] == 422 for p in snap["plans"].values() if "error" in p)
    day = "syn-2025-08-03-co_occurring"
    assert snap["plans"][day] == client.post("/api/plan", json={"day_id": day}).json()  # same as the live API
    assert snap["default_params"] == {"paid_hours": 8.5, "earliest": "04:00", "latest": "19:00", "oracle": False}
    path = snapshot.main(tmp_path / "snapshot.json")
    assert json.loads(path.read_text(encoding="utf-8"))["days"] == snap["days"]


def test_rule_selects_real_day_with_most_dual_hazard_hours(monkeypatch):
    days = planning.load_days()
    fake = [d.model_copy(update={"id": f"real-{d.date}-testregion", "region": "testregion",
                                 "provenance": "real_cached"}) for d in days if "co_occurring" in d.id or "mild" in d.id]
    monkeypatch.setattr(planning, "load_days", lambda: tuple(days) + tuple(fake))
    monkeypatch.setattr(main, "load_days", planning.load_days)
    planning.rule_selected_day.cache_clear()
    try:
        listed = client.get("/api/days").json()
        chosen = [d for d in listed if "selected_by_rule" in d]
        assert [d["id"] for d in chosen] == ["real-2025-08-03-testregion"]  # co_occurring has the most dual hours
        assert "selected for illustration by rule" in chosen[0]["selected_by_rule"]
    finally:
        planning.rule_selected_day.cache_clear()  # without real days nothing is selected (see test_api key check)


def test_ui_has_replay_and_snapshot_banners():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    for s in ("REPLAY: recorded data, not live", "SNAPSHOT MODE: sliders disabled", "fetch('snapshot.json')",
              "What this does and does not show", "robust (scenario-averaged)"):
        assert s in html
