"""Vercel deploy: the config routes every API path to the one function, and the committed files are enough to run it."""
import json
from pathlib import Path

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
CONF = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))


def test_every_api_route_is_rewritten_to_the_function():
    from app.main import app
    sources = {r["source"] for r in CONF["rewrites"] if r["destination"] == "/api/index"}
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path != "/":
            assert "/api/:path*" in sources if route.path.startswith("/api/") else route.path in sources, route.path
    assert {"source": "/", "destination": "/static/index.html", "permanent": False} in CONF["redirects"]
    assert CONF["framework"] is None and "api/index.py" in CONF["functions"]


def test_entry_point_exposes_the_same_app():
    from api.index import app as vercel_app
    from app.main import app
    assert vercel_app is app


def test_real_day_records_are_committed_and_small():
    assert "!data/cache/real-*.json" in (ROOT / ".gitignore").read_text(encoding="utf-8")
    files = sorted((ROOT / "data" / "cache").glob("real-*.json"))
    assert (ROOT / "data" / "cache" / "real-2024-07-14-bakersfield.json") in files  # the demo's default day
    assert sum(f.stat().st_size for f in files) < 20_000_000


def test_largest_response_fits_the_function_payload_limit():
    from app.main import app
    body = TestClient(app).get("/api/eval").content
    assert len(body) < 4_500_000  # Vercel function response limit
