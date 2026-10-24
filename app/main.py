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
EVAL_W2 = Path(__file__).resolve().parent.parent / "eval" / "results_w2.json"
START_FILES = {w: Path(__file__).resolve().parent.parent / "analysis" / f
               for w, f in (("window1", "start_sensitivity.json"), ("window2", "start_sensitivity_w2.json"))}

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


def _results(path: Path, run_hint: str, drop_days: bool = False) -> dict:
    if not path.exists():
        return {"available": False, "reason": f"{path.parent.name}/{path.name} not found; run {run_hint}"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"available": False, "reason": f"{path.name} unreadable: {e.__class__.__name__}"}
    return {"available": True, **({k: v for k, v in data.items() if k != "days"} if drop_days else data)}


@app.get("/api/eval")
def api_eval() -> dict:
    return _results(EVAL_RESULTS, "python eval/run_eval.py")


@app.get("/api/eval_w2")
def api_eval_w2() -> dict:
    """PREREGISTERED (WINDOW 2) aggregates; the per-day appendix stays in eval/results_w2.json."""
    return _results(EVAL_W2, "python -m analysis.eval_window2", drop_days=True)


@app.get("/api/start_sensitivity")
def api_start_sensitivity() -> dict:
    """EXPLORATORY, POST-HOC: start-time sensitivity for each window (null if not computed)."""
    out = {"label": "EXPLORATORY, POST-HOC: not preregistered"}
    for w, path in START_FILES.items():
        out[w] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    return out


@app.get("/crew-sheet", response_class=HTMLResponse)
def crew_sheet(request: Request) -> HTMLResponse:
    try:
        req = PlanRequest(**dict(request.query_params))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=[err["msg"] for err in e.errors()])
    return HTMLResponse(render(_plan(req)))


app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
