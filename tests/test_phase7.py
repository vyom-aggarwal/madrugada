"""Phase 7: exploratory outputs, demo snapshot and pitch fill are consistent with the committed results."""
import json
import re
from pathlib import Path

from analysis import fill_pitch
from eval import prereg

ROOT = Path(__file__).resolve().parent.parent


def test_preregistration_still_matches():
    assert prereg.verify() == (True, [])


def test_exploratory_findings_labeled():
    first = (ROOT / "docs" / "exploratory_findings.md").read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("EXPLORATORY, POST-HOC: NOT PREREGISTERED.")
    assert json.loads((ROOT / "analysis" / "exploratory_results.json").read_text(encoding="utf-8"))["label"] == \
        "EXPLORATORY, POST-HOC: not preregistered"


def test_demo_snapshot_small_and_rule_stated():
    path = ROOT / "static" / "demo_snapshot.json"
    snap = json.loads(path.read_text(encoding="utf-8"))
    assert path.stat().st_size < 1.5e6 and 0 < len(snap["days"]) <= 24
    assert set(snap["plans"]) == {d["id"] for d in snap["days"]}
    assert all(d["provenance"] == "real_cached" for d in snap["days"])
    assert "selected for illustration" in snap["selection_rule"].lower() and "days" not in snap["eval"]
    assert sum("selected_by_rule" in d for d in snap["days"]) == 1


def test_pitch_fills_without_placeholders():
    v = fill_pitch.values()
    template = (ROOT / "docs" / "PITCH.md").read_text(encoding="utf-8")
    assert set(re.findall(r"\{\{(\w+)\}\}", template)) <= set(v)
    assert not re.search(r"-?\d+\.\d{2,}", re.sub(r"\{\{\w+\}\}", "", template))  # no hardcoded results


def test_ui_claim_copy():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert "Heat-first shift planner with smoke exposure shown" in html and "demo_snapshot.json" in html
    assert "modeled" in html and "Not a compliance tool" in html
