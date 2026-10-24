"""FastAPI entry point: static UI, day list, plan endpoint, backtest results, printable crew sheet."""
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.crew_sheet import render
from app.models import PlanRequest
from app.planning import RULE_LABEL, NoHistory, UnknownDay, day_summary, load_days, plan_for, rule_selected_day

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
EVAL_RESULTS = Path(__file__).resolve().parent.parent / "eval" / "results.json"

app = FastAPI(title="Madrugada", version="0.3.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/static/index.html")


@app.get("/api/days")
def api_days() -> list[dict]:
    selected = rule_selected_day()
    return [{**day_summary(d), **({"selected_by_rule": RULE_LABEL} if d.id == selected else {})}
            for d in load_days()]


def _plan(req: PlanRequest) -> dict:
    try:
        return plan_for(req.day_id, req.paid_hours, req.earliest, req.latest, req.oracle)
    except UnknownDay:
        raise HTTPException(status_code=404, detail="Day not found: no day with that day_id. "
                                                    "GET /api/days lists the available days.")
    except NoHistory as e:
        raise HTTPException(status_code=422, detail=f"no forecast history for this day: {e}")


@app.post("/api/plan")
def api_plan(req: PlanRequest) -> dict:
    return _plan(req)


@app.get("/api/eval")
def api_eval() -> dict:
    if not EVAL_RESULTS.exists():
        return {"available": False, "reason": "eval/results.json not found; run python eval/run_eval.py"}
    try:
        return {"available": True, **json.loads(EVAL_RESULTS.read_text(encoding="utf-8"))}
    except (OSError, ValueError) as e:
        return {"available": False, "reason": f"eval/results.json unreadable: {e.__class__.__name__}"}


@app.get("/crew-sheet", response_class=HTMLResponse)
def crew_sheet(request: Request) -> HTMLResponse:
    try:
        req = PlanRequest(**dict(request.query_params))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=[err["msg"] for err in e.errors()])
    return HTMLResponse(render(_plan(req)))


app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
