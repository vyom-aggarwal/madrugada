"""Claims audit: forbidden phrases, unfilled pitch placeholders, and headline numbers vs their source JSON."""
import re
from pathlib import Path

import pytest

from analysis import fill_pitch

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = ["keeps workers safe", "keep workers safe", "keeping workers safe", "protects workers", "protect workers",
             "prevents heat illness", "prevent heat illness", "prevents illness", "saves lives", "save lives",
             "ensures compliance", "ensure compliance", "guarantees", "guaranteed", "beats heat-only",
             "outperforms heat-only", "wage-neutral guarantee"]


def _scanned() -> list[Path]:
    files = [p for p in (ROOT / "static").rglob("*") if p.is_file() and p.name != "snapshot.json"]
    files += sorted((ROOT / "app").glob("*.py")) + sorted((ROOT / "docs").glob("PITCH*.md")) + [ROOT / "README.md"]
    return files


@pytest.mark.parametrize("path", _scanned(), ids=lambda p: str(p.relative_to(ROOT)))
def test_no_forbidden_phrases(path):
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    hits = [p for p in FORBIDDEN if p in text]
    assert not hits, f"{path.name}: {hits}"


def test_pitch_has_no_unreplaced_placeholders():
    fill_pitch.main()
    assert not re.search(r"\{\{\w+\}\}", (ROOT / "docs" / "PITCH_filled.md").read_text(encoding="utf-8"))


def test_headline_numbers_match_source_json():
    """Recompute each headline string straight from the JSON (independent of fill_pitch.fmt) and require it."""
    text = (ROOT / "docs" / "PITCH_filled.md").read_text(encoding="utf-8")
    src = fill_pitch.sources()
    checked = 0
    for key, item in src.items():
        if not key.startswith("w"):
            continue
        c, k = item[0], item[1]
        d = item[2] if len(item) > 2 else {"hours_ge_95f": 2, "hours_aqi_ge_101": 3}[k]
        mean = f"{c['mean_diff'][k]:+.{d}f} h/day"
        lo, hi = (f"{x:+.{d}f}" for x in c["ci95"][k])
        assert f"{mean} (CI {lo} to {hi})" in text, f"{key}: {mean} [{lo}, {hi}] not quoted exactly"
        checked += 1
    assert checked >= 9
    # integer headline counts, read straight from the JSON
    for res in (src["r1"], src["r2"]):
        o = res["groups"]["real_cached"]["overall"]["comparisons"]["optimizer_vs_B2"]
        assert f"{o['n']} region-days" in text
