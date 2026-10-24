"""FastAPI entry point: static UI, day list, plan endpoint, printable crew sheet."""
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.crew_sheet import render
from app.models import PlanRequest
from app.planning import NoHistory, UnknownDay, day_summary, load_days, plan_for

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Madrugada", version="0.3.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/static/index.html")


@app.get("/api/days")
def api_days() -> list[dict]:
    return [day_summary(d) for d in load_days()]


def _plan(req: PlanRequest) -> dict:
    try:
        return plan_for(req.day_id, req.paid_hours, req.earliest, req.latest, req.oracle)
    except UnknownDay:
        raise HTTPException(status_code=404, detail="unknown day_id")
    except NoHistory as e:
        raise HTTPException(status_code=422, detail=f"no forecast history for this day: {e}")


@app.post("/api/plan")
def api_plan(req: PlanRequest) -> dict:
    return _plan(req)


@app.get("/crew-sheet", response_class=HTMLResponse)
def crew_sheet(request: Request) -> HTMLResponse:
    try:
        req = PlanRequest(**dict(request.query_params))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=[err["msg"] for err in e.errors()])
    return HTMLResponse(render(_plan(req)))


app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
