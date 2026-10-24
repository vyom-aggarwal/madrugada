"""Build static/snapshot.json: /api/days, /api/eval and the default-parameter /api/plan result for every day,
or (demo) the small committed static/demo_snapshot.json.

index.html falls back to snapshot.json (SNAPSHOT MODE) when an API call fails, and to demo_snapshot.json when
snapshot.json is missing. Calls the same handler functions the API uses, so the content matches the live responses.
Run: python -m app.snapshot [demo]   (or: python tasks.py snapshot / python tasks.py demo_snapshot)
"""
import json
import random
from pathlib import Path

import numpy as np
from fastapi import HTTPException

from app.exposure import day_arrays, exposure
from app.main import STATIC_DIR, _plan, api_days, api_eval, api_eval_w2, api_start_sensitivity
from app.models import PlanRequest
from app.planning import get_day, rule_selected_day

SNAPSHOT_PATH = STATIC_DIR / "snapshot.json"
DEMO_PATH = STATIC_DIR / "demo_snapshot.json"
DEMO_SEED = 20261024
DEMO_RULE = ("Selected for illustration; the evaluation uses all days. From the evaluated real days: (1) the "
             "rule-selected default day (most observed dual-hazard hours), then (2) the top 6 by observed hours >=95F, "
             "(3) the top 6 by observed AQI>=101 hours, (4) 6 mild-stratum days by a fixed-seed draw (seed "
             f"{DEMO_SEED}), (5) a fixed-seed draw from the rest to reach 24. Ties: earlier date, then id. "
             "Days already picked are skipped.")


def build() -> dict:
    days = api_days()
    plans = {}
    for d in days:
        try:
            plans[d["id"]] = _plan(PlanRequest(day_id=d["id"]))
        except HTTPException as e:  # e.g. no forecast history: keep the API's message
            plans[d["id"]] = {"error": e.detail, "status": e.status_code}
    return {"generated_by": "tasks.py snapshot",
            "default_params": PlanRequest(day_id="-").model_dump(exclude={"day_id"}),
            "days": days, "eval": api_eval(), "eval_w2": api_eval_w2(), "start_sensitivity": api_start_sensitivity(),
            "plans": plans}


def _demo_days(evaluated: list[dict]) -> list[str]:
    hours = {}
    for d in evaluated:
        t, a = day_arrays(get_day(d["id"]))
        m = exposure(t, a, np.ones(len(t), bool))
        hours[d["id"]] = (m.hours_ge_95f, m.hours_aqi_ge_101)
    order = sorted(evaluated, key=lambda d: (d["date"], d["id"]))
    picks = [rule_selected_day()] if rule_selected_day() in hours else []

    def take(cands, n):
        for c in [c for c in cands if c not in picks][:n]:
            picks.append(c)
    take([d["id"] for d in sorted(order, key=lambda d: -hours[d["id"]][0])], 6)
    take([d["id"] for d in sorted(order, key=lambda d: -hours[d["id"]][1])], 6)
    rng = random.Random(DEMO_SEED)
    mild = [d["id"] for d in order if d["stratum"] == "mild" and d["id"] not in picks]
    take(rng.sample(mild, min(6, len(mild))), 6)
    rest = [d["id"] for d in order if d["id"] not in picks]
    take(rng.sample(rest, min(24 - len(picks), len(rest))), 24 - len(picks))
    return picks


def build_demo() -> dict:
    """Small committed snapshot: eval aggregates (no per-day appendix) + plans for <= 24 real days."""
    ev = api_eval()
    evaluated = [d for d in ev.get("days", []) if d["provenance"] == "real_cached"]
    ids = _demo_days(evaluated)
    days = [d for d in api_days() if d["id"] in set(ids)]
    days.sort(key=lambda d: ids.index(d["id"]))
    return {"generated_by": "tasks.py demo_snapshot", "selection_rule": DEMO_RULE,
            "note": "demo subset: 24 real days selected for illustration; the evaluation uses all days",
            "default_params": PlanRequest(day_id="-").model_dump(exclude={"day_id"}), "days": days,
            "eval": {k: v for k, v in ev.items() if k != "days"}, "eval_w2": api_eval_w2(),
            "start_sensitivity": api_start_sensitivity(),
            "plans": {i: _plan(PlanRequest(day_id=i)) for i in ids}}


def main(path: Path = SNAPSHOT_PATH) -> Path:
    snap = build()
    path.write_text(json.dumps(snap, separators=(",", ":")), encoding="utf-8")
    ok = sum("error" not in p for p in snap["plans"].values())
    print(f"wrote {path}: {len(snap['days'])} days, {ok} plans, eval available={snap['eval'].get('available')}")
    return path


def main_demo(path: Path = DEMO_PATH) -> Path:
    snap = build_demo()
    path.write_text(json.dumps(snap, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {path}: {len(snap['days'])} days, {path.stat().st_size / 1e6:.2f} MB")
    return path


if __name__ == "__main__":
    import sys
    main_demo() if sys.argv[1:] == ["demo"] else main()
