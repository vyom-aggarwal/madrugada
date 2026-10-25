"""Vercel deploy: the config routes every API path to the one function, and the committed files are enough to run it."""
import json
import re
from pathlib import Path

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
CONF = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))


def test_every_api_route_is_rewritten_to_the_function():
    from app.main import app
    sources = {r["source"] for r in CONF["rewrites"] if r["destination"] == "/api/index"}
    to_static = {r["source"] for r in CONF["rewrites"] if r["destination"].startswith("/static/")}  # served by the CDN
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path != "/" and route.path not in to_static:
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


def test_favicon_files_exist_and_are_linked():
    static = ROOT / "static"
    html = (static / "index.html").read_text(encoding="utf-8")
    for name in ["favicon.ico", "favicon.svg", "apple-touch-icon.png", "site.webmanifest"]:
        assert (static / name).exists() and f'href="{name}"' in html, name
    assert not re.search(r'<link rel="(icon|apple-touch-icon|manifest)" href="data:', html)  # the old inline icon broke on its quotes
    ico = (static / "favicon.ico").read_bytes()
    assert ico[:4] == b"\x00\x00\x01\x00" and ico[4] == 3  # ICO with 16, 32 and 48 px images
    for icon in json.loads((static / "site.webmanifest").read_text(encoding="utf-8"))["icons"]:
        assert (static / icon["src"]).exists(), icon["src"]
    from app.main import app
    r = TestClient(app).get("/favicon.ico")
    assert r.status_code == 200 and r.content == ico
    assert {"source": "/favicon.ico", "destination": "/static/favicon.ico"} in CONF["rewrites"]
