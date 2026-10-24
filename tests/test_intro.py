"""Opening sequence: the pure timeline, skip and wording functions (run in node), and no hardcoded result numbers."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
NODE = shutil.which("node")


def block(script_id: str) -> str:
    return re.search(rf'<script id="{script_id}">(.*?)</script>', HTML, re.S).group(1)


HARNESS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8'), snap = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const m = new Function(src + '; return {CINE_SCENES, cineTimeline, cineAdvance, cineMode, cineKey, cinePresent, cineHoldAt, cineSkipVisible, cineType, storyParts, story, startVerdict};')();
const T = m.cineTimeline(m.CINE_SCENES), P = m.storyParts(snap.eval, snap.eval_w2, snap.start_sensitivity), st = snap.start_sensitivity.window1.settings;
console.log(JSON.stringify({
  total: T.total, starts: T.starts, at0: T.at(0), at5: T.at(5), atEnd: T.at(T.total + 9), atNeg: T.at(-3),
  prevMid: T.prev(7.5), prevEarly: T.prev(5.4), prev0: T.prev(0.3), next0: T.next(0.2), nextLast: T.next(T.total - 1),
  adv: m.cineAdvance(1, 0.05, true, T.total), paused: m.cineAdvance(1, 0.05, false, T.total),
  stall: m.cineAdvance(1, 5, true, T.total), end: m.cineAdvance(T.total - 0.01, 0.05, true, T.total),
  modes: [['?intro=0', false], ['?intro=1', false], ['', false], ['', true], ['?intro=0', true], ['?intro=1', true]].map(a => m.cineMode(...a)),
  keys: ['Escape', 'Enter', ' ', 'ArrowLeft', 'ArrowRight', 'a'].map(k => m.cineKey(k)),
  pkeys: ['Escape', 'Enter', ' ', 'ArrowLeft', 'ArrowRight', 'PageDown', 'PageUp'].map(k => m.cineKey(k, true)),
  present: ['?present=1', '?present=0', ''].map(m.cinePresent), holds: [0, 6, 42].map(t => m.cineHoldAt(T, m.CINE_SCENES, t)),
  held: m.cineAdvance(4.5, 0.1, true, T.total, 4.55),
  skip: [0, 0.49, 0.5].map(m.cineSkipVisible), type: [0, 0.5, 2].map(p => m.cineType('abcd', p)),
  P: P && {heat: P.heat, replicated: P.replicated, smokeW2: P.smokeW2, vsB3: P.vsB3},
  story: m.story(snap.eval, snap.eval_w2, snap.start_sensitivity), none: m.story(null, null, {}), noneP: m.storyParts(null, null, {}),
  verdicts: Object.fromEntries(Object.keys(st).map(k => [k, m.startVerdict(st[k].groups.overall.optimizer_vs_B2)])),
  synthetic: [[-1, -0.1], [0.1, 0.2], [-0.1, 0.2]].map(ci => m.startVerdict({ci95: {hours_ge_95f: ci}})).concat([m.startVerdict(null)]),
}));
"""


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    if not NODE:
        pytest.skip("node is not installed")
    d = tmp_path_factory.mktemp("intro")
    (d / "core.js").write_text(block("intro-core"), encoding="utf-8")
    (d / "harness.js").write_text(HARNESS, encoding="utf-8")
    r = subprocess.run([NODE, str(d / "harness.js"), str(d / "core.js"), str(ROOT / "static" / "demo_snapshot.json")],
                       capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_timeline_seek(out):
    assert out["total"] == 43 and out["starts"] == [0, 5, 12, 18, 26, 33, 38]
    assert out["at0"] == {"i": 0, "local": 0, "p": 0}
    assert out["at5"]["i"] == 1 and out["at5"]["local"] == 0
    assert out["atEnd"]["i"] == 6 and out["atEnd"]["p"] == 1 and out["atNeg"]["i"] == 0  # seeks clamp to the timeline
    assert (out["prevMid"], out["prevEarly"], out["prev0"]) == (5, 0, 0)  # Back restarts a scene, or goes back one near its start
    assert (out["next0"], out["nextLast"]) == (5, 43)


def test_master_clock(out):
    assert out["adv"]["t"] == pytest.approx(1.05) and not out["adv"]["ended"]
    assert out["paused"]["t"] == 1  # paused clock does not move
    assert out["stall"]["t"] == pytest.approx(1.1)  # a stalled tab never jumps a scene
    assert out["end"]["ended"] is True


def test_modes_keys_and_skip(out):
    assert out["modes"] == ["off", "motion", "motion", "static", "off", "static"]
    assert out["keys"] == ["skip", "skip", "toggle", "prev", "next", None]  # Esc and Enter skip from 0 s
    assert out["skip"] == [False, False, True]  # the Skip button shows from 0.5 s
    assert out["type"] == ["", "ab", "abcd"]


def test_wording_is_chosen_from_the_cis(out):
    assert out["P"]["heat"] == "It does only if crews can start before dawn (04:00)"
    assert out["P"]["replicated"] is True
    assert out["P"]["smokeW2"].startswith("small reduction vs the early fixed shift in window 2")
    assert out["P"]["vsB3"] == "none vs heat-only planning"
    assert out["story"].startswith(out["P"]["heat"] + ": vs the fixed 05:30 shift, -0.377")
    assert out["none"] == "Real-data results are not available." and out["noneP"] is None
    assert out["verdicts"]["04:00"] == "still fewer high-heat hours" and out["verdicts"]["06:00"].startswith("no reduction left")
    assert out["synthetic"] == ["still fewer high-heat hours", "no reduction left (slightly more high-heat hours)", "about zero: no clear change", "not computed"]


def test_intro_numbers_are_read_at_runtime():
    text = block("intro-cine")
    for lit in ["1,296", "1296", "768", "0.38", "0.377", "8.5", "3.5", "80°F", "95°F", "AQI 151", "05:30", "07:00"]:
        assert lit not in text, lit


def test_presenter_mode_holds_each_scene(out):
    assert out["pkeys"] == ["skip", "next", "next", "prev", "next", "next", "prev"]  # a clicker never exits by accident
    assert out["present"] == [True, False, False]
    assert out["holds"] == pytest.approx([4.55, 11.55, 42.99])  # just before each fade-out; the last on its prompt
    assert out["held"]["t"] == pytest.approx(4.55) and out["held"]["held"] is True and not out["held"]["ended"]
