"""Evaluation harness: strata, bootstrap, config immutability, end-to-end run, /api/eval."""
import copy
import json
import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import load_config
from app.exposure import day_arrays
from app.models import DayRecord
from eval import metrics, run_eval, stats


def _day(temp, pm):
    return DayRecord(id="x", label="hand-built", region="r", provenance="synthetic",
                     temp_f=[70.0] * 95 + [temp], rh=[30.0] * 96, solar_wm2=[0.0] * 96, pm25_ugm3=[5.0] * 95 + [pm])


@pytest.mark.parametrize("temp, pm, expected", [
    (95.0, 5.0, "heat_only"), (94.9, 40.0, "smoke_only"), (100.0, 60.0, "co_occurring"),
    (94.9, 35.4, "mild"), (95.0, 35.5, "co_occurring"),  # PM 35.4 -> AQI 100, 35.5 -> AQI 101
])
def test_strata_rule_on_hand_built_days(temp, pm, expected):
    assert metrics.stratum(*day_arrays(_day(temp, pm))) == expected


def test_bootstrap_deterministic_and_skipped_for_small_n():
    d = np.random.default_rng(0).normal(size=12)
    assert stats.paired_bootstrap_ci(d, 10000, 7) == stats.paired_bootstrap_ci(d, 10000, 7)
    plan = {k: 0.0 for k in metrics.PHYS} | {"observed_cost": 0.0}
    days = [{"plans": {"optimizer": plan, "B2": {**plan, "observed_cost": 1.0}}}] * 9
    r = stats.compare(days, "optimizer", "B2", load_config())
    assert r["ci95"] is None and r["ci_note"] == "n too small for CIs"
    assert r["cost"]["win"] == 9 and r["physical"]["tie"] == 9  # same hours, different cost
    r10 = stats.compare(days + days[:1], "optimizer", "B2", load_config())
    assert r10["ci95"]["observed_cost"] == (-1.0, -1.0)


def test_classify_tie_and_mixed():
    cfg = load_config()
    a = {k: 1.0 for k in metrics.PHYS} | {"observed_cost": 5.0}
    assert metrics.classify(a, dict(a), cfg) == "tie"
    assert metrics.classify(a, {**a, "hours_ge_80f": 2.0}, cfg) == "mixed"
    assert metrics.classify(a, {**a, "observed_cost": 6.0}, cfg) == "win"


@pytest.mark.parametrize("d95, d101, other, expected", [
    (0, 0, 0, "tie"), (-0.25, 0, 0, "win"), (0, -1.0, 0, "win"), (0.25, 0, 0, "loss"), (0, 0.5, 0, "loss"),
    (-0.25, 0.25, 0, "mixed"), (0, 0, 1.0, "mixed"),  # equal 95F/101 hours, other metric differs
])
def test_classify_physical(d95, d101, other, expected):
    base = {k: 2.0 for k in metrics.PHYS} | {"observed_cost": 0.0}
    a = {**base, "hours_ge_95f": 2.0 + d95, "hours_aqi_ge_101": 2.0 + d101, "hours_ge_80f": 2.0 + other}
    assert metrics.classify_physical(a, base, load_config()) == expected


def test_sensitivity_does_not_mutate_global_config(test_days, history):
    cfg = load_config()
    snapshot = copy.deepcopy(cfg)
    pool = history + test_days
    settings = metrics.sensitivity_settings(cfg)
    assert len(settings) == 81 and all(c is not cfg for _, c in settings)
    d = test_days[0]
    ft, fa = metrics.forecast_arrays(d, pool, cfg)
    ot, oa = day_arrays(d)
    metrics.weight_sensitivity([{"id": d.id, "stratum": "x", "provenance": d.provenance,
                                 "ft": ft, "fa": fa, "ot": ot, "oa": oa}], cfg)
    metrics.forecast_sensitivity(test_days[:2], pool, cfg)
    assert load_config() is cfg and cfg == snapshot


def test_eval_end_to_end(tmp_path):
    snapshot = copy.deepcopy(load_config())
    start = time.perf_counter()
    res = run_eval.run()
    assert time.perf_counter() - start < 15
    assert load_config() == snapshot
    j, m = run_eval.write(res, tmp_path)
    first = m.read_text(encoding="utf-8").splitlines()[0]
    assert first == res["provenance_statement"]
    assert first.startswith("SYNTHETIC DAYS INCLUDED: NOT EVIDENCE FOR THE DUAL-HAZARD CLAIM")
    assert "insufficient real days" in first
    assert res["n_days"] == {"synthetic": 13, "real_cached": 0}  # every day with proxy history
    assert {d["stratum"] for d in res["days"]} <= set(metrics.STRATA)
    assert all(set(d["plans"]) == set(metrics.PLANS) for d in res["days"])
    od = res["oracle_diagnosis"]["synthetic"]
    assert "losses become oracle wins" in od["physical"]["sentence"] and "become ties" in od["cost"]["sentence"]
    assert "Heat-only planning is the closest baseline; see the B3 rows." in res["summary_box"]
    fb = set(res["robust_fallback_days"]["synthetic"])
    n_robust = res["groups"]["synthetic"]["overall"]["comparisons"]["robust_vs_B2"]["n"]
    assert n_robust == 13 - len(fb) and all(d["robust_flags"] for d in res["days"] if d["id"] in fb)
    if not any(stats.b3_smoke_wins(res["days"], load_config()).values()):
        assert any("never has fewer AQI>=101 hours than either B3" in s for s in res["summary_box"])
    assert json.loads(j.read_text(encoding="utf-8"))["n_days"]["synthetic"] == 13


def test_api_eval(monkeypatch, tmp_path):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "EVAL_RESULTS", tmp_path / "missing.json")
    r = client.get("/api/eval").json()
    assert r["available"] is False and r["reason"]
    path = tmp_path / "results.json"
    path.write_text(json.dumps({"provenance_statement": "SYNTHETIC DAYS INCLUDED", "n_days": {}}), encoding="utf-8")
    monkeypatch.setattr(main, "EVAL_RESULTS", path)
    r = client.get("/api/eval").json()
    assert r["available"] is True and r["provenance_statement"] == "SYNTHETIC DAYS INCLUDED"
