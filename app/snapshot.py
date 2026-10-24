"""Build static/snapshot.json: /api/days, /api/eval and the default-parameter /api/plan result for every day.

index.html falls back to this file (SNAPSHOT MODE) when an API call fails. Calls the same handler
functions the API uses, so the content is identical to the live responses.
Run: python -m app.snapshot   (or: python tasks.py snapshot)
"""
import json
from pathlib import Path

from fastapi import HTTPException

from app.main import STATIC_DIR, _plan, api_days, api_eval
from app.models import PlanRequest

SNAPSHOT_PATH = STATIC_DIR / "snapshot.json"


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
            "days": days, "eval": api_eval(), "plans": plans}


def main(path: Path = SNAPSHOT_PATH) -> Path:
    snap = build()
    path.write_text(json.dumps(snap, separators=(",", ":")), encoding="utf-8")
    ok = sum("error" not in p for p in snap["plans"].values())
    print(f"wrote {path}: {len(snap['days'])} days, {ok} plans, eval available={snap['eval'].get('available')}")
    return path


if __name__ == "__main__":
    main()
