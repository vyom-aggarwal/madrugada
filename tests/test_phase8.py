"""Phase 8: start-time sensitivity, window-2 preregistration and isolation, new endpoints. No network."""
import json
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from analysis import eval_window2, fetch_window2, prereg2
from analysis.sensitivity_start import SETTINGS, sunrise_local, sunrise_start
from app import main
from app.config import load_config
from eval import prereg

ROOT = Path(__file__).resolve().parent.parent


def test_sunrise_approximation_is_plausible():
    t = sunrise_local(date(2024, 6, 21), 36.78, -119.72)  # Fresno, summer solstice: about 05:40 PDT
    assert (t.hour, t.utcoffset().total_seconds()) == (5, -7 * 3600) and 35 <= t.minute <= 45
    assert sunrise_start(date(2024, 6, 21), 36.78, -119.72, load_config()) == "05:15"


def test_preregistration_2_hashes_equal_window_1():
    assert prereg.verify() == (True, [])
    assert prereg.verify(prereg2.PREREG2) == (True, [])
    assert prereg2.recorded(prereg2.PREREG2) == prereg2.recorded(prereg.PREREG_PATH)
    text = prereg2.PREREG2.read_text(encoding="utf-8")
    assert "NEVER pooled" in text and "2018, 2019, 2020, 2021" in text


def test_window2_scripts_refuse_without_matching_preregistration(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_window2, "PREREG2", tmp_path / "missing.md")
    monkeypatch.setattr(fetch_window2, "PREREG2", tmp_path / "missing.md")
    assert eval_window2.main() == 4 and fetch_window2.main() == 4


def test_window2_cache_is_separate():
    assert fetch_window2.CACHE_W2 != ROOT / "data" / "cache" and eval_window2.CACHE_W2 == fetch_window2.CACHE_W2


def test_start_sensitivity_outputs_labeled():
    st = json.loads((ROOT / "analysis" / "start_sensitivity.json").read_text(encoding="utf-8"))
    assert st["label"] == "EXPLORATORY, POST-HOC: not preregistered" and list(st["settings"]) == SETTINGS
    assert (ROOT / "docs" / "start_sensitivity.md").read_text(encoding="utf-8").startswith(
        "EXPLORATORY, POST-HOC: NOT PREREGISTERED")


def test_results_w2_labeled_and_never_pooled():
    path = ROOT / "eval" / "results_w2.json"
    if not path.exists():
        return
    first = (ROOT / "docs" / "results_w2.md").read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("PREREGISTERED (WINDOW 2): SUMMERS 2018 TO 2021")
    r = json.loads(path.read_text(encoding="utf-8"))
    assert all(d["date"] < "2022-01-01" for d in r["days"]) and r["n_days"]["synthetic"] == 0


def test_window_endpoints():
    c = TestClient(main.app)
    w2 = c.get("/api/eval_w2").json()
    assert "available" in w2 and "days" not in w2
    st = c.get("/api/start_sensitivity").json()
    assert st["label"].startswith("EXPLORATORY") and st["window1"]["n_days"] > 0
