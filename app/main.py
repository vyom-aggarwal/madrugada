"""FastAPI entry point. Phase 0: static files and health check only."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Madrugada", version="0.0.1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
