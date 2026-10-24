"""Phase 3 API, crew sheet and static UI checks via TestClient (no network)."""
import re
import time

import pytest
from fastapi.testclient import TestClient

from app import planning
from app.main import app, STATIC_DIR
from tests.conftest import load_raw

client = TestClient(app)
DAY = "syn-2025-08-03-co_occurring"
FIRST_HISTORY = "syn-2025-07-18-history"


def _plan(**kw):
    return client.post("/api/plan", json={"day_id": DAY, **kw})


def test_days_lists_all_fixtures_with_provenance():
    r = client.get("/api/days")
    assert r.status_code == 200
    got = {d["id"]: d for d in r.json()}
    for d in load_raw("days.json") + load_raw("history.json"):
        assert got[d["id"]]["provenance"] == d["provenance"] == "synthetic"
        assert set(got[d["id"]]) == {"id", "label", "date", "provenance"}


def test_plan_happy_path():
    planning.plan_for.cache_clear()
    start = time.perf_counter()
    r = _plan(paid_hours=7.3)
    elapsed = time.perf_counter() - start
    assert r.status_code == 200 and elapsed < 2.0
    j = r.json()
    assert {"day", "mode", "forecast", "plan", "plans", "metrics", "pareto", "warnings"} <= set(j)
    assert j["day"]["provenance"] == "synthetic" and j["mode"] == "proxy"
    assert len(j["forecast"]["temp_f"]) == len(j["forecast"]["aqi"]) == 96
    assert j["plan"]["paid_hours"] >= 7.3
    assert set(j["plans"]) == set(j["metrics"]) == {"optimizer", "robust", "B1", "B2", "b3_early", "b3_late"}
    assert all(set(m) == {"planned", "observed"} for m in j["metrics"].values())
    assert j["pareto"] and all("blocks" in p for p in j["pareto"])
    assert any("SYNTHETIC" in w for w in j["warnings"])
    start = time.perf_counter()
    assert _plan(paid_hours=7.3).json() == j  # cached
    assert time.perf_counter() - start < 0.2


@pytest.mark.parametrize("body", [
    {"paid_hours": 1.5}, {"paid_hours": 12.5}, {"earliest": "12:00", "latest": "10:00"},
    {"earliest": "10:00", "latest": "14:00", "paid_hours": 8.5}, {"earliest": "4am"}, {"earliest": "04:10"},
])
def test_invalid_inputs_422(body):
    r = _plan(**body)
    assert r.status_code == 422 and r.json()["detail"]


def test_unknown_day_404_and_no_history_422():
    assert client.post("/api/plan", json={"day_id": "nope"}).status_code == 404
    r = client.post("/api/plan", json={"day_id": FIRST_HISTORY})
    assert r.status_code == 422 and "needs prior days" in r.json()["detail"]


def test_oracle_mode():
    j = _plan(oracle=True).json()
    assert j["mode"] == "ORACLE" and any("ORACLE" in w for w in j["warnings"])


def test_crew_sheet_content():
    r = client.get("/crew-sheet", params={"day_id": DAY, "paid_hours": 8.5, "earliest": "04:00",
                                          "latest": "19:00", "oracle": "true"})
    assert r.status_code == 200
    t = r.text
    assert "does not replace" in t and "Heat Illness Prevention Plan" in t and "No reemplaza" in t
    assert "Data: SYNTHETIC illustration" in t and "Spanish text needs native-speaker review." in t
    assert "forecast-based estimate" in t and "ORACLE: upper bound" in t and " AM" in t


def test_crew_sheet_rejects_bad_params():
    hostile = "<script>alert(1)</script>"
    r = client.get("/crew-sheet", params={"day_id": hostile})
    assert r.status_code == 404 and "<script>" not in r.text
    r = client.get("/crew-sheet", params={"day_id": DAY, "earliest": hostile})
    assert r.status_code == 422 and "<script>alert" not in r.text.replace("\\u003c", "")


def test_crew_sheet_escapes_hostile_label(monkeypatch):
    hostile = '<script>alert("x")</script>'
    days = tuple(d.model_copy(update={"label": hostile}) if d.id == DAY else d for d in planning.load_days())
    monkeypatch.setattr(planning, "load_days", lambda: days)
    planning.plan_for.cache_clear()
    try:
        r = client.get("/crew-sheet", params={"day_id": DAY})
        assert r.status_code == 200
        assert "<script>alert" not in r.text and "&lt;script&gt;alert(&quot;x&quot;)" in r.text
    finally:
        planning.plan_for.cache_clear()


def test_index_loads_and_js_ids_exist():
    r = client.get("/static/index.html")
    assert r.status_code == 200
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = html.split("<script>")[1]
    used = set(re.findall(r"\$\('([\w-]+)'\)", script)) | set(re.findall(r"getElementById\('([\w-]+)'\)", script))
    used |= set(re.findall(r"'([\w-]+)'", script.split("forEach(id =>")[0].split("[")[-1]))
    defined = set(re.findall(r'id="([\w-]+)"', html))
    assert used and used <= defined, used - defined
    assert "Not a compliance tool and not a health prediction." in html
    assert not re.search(r"<script[^>]+src=|<link[^>]+href=\"http", html)  # offline: no external resources
    assert "keeps workers safe" not in html.lower()
