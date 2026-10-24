"""Vercel entry point: the FastAPI app as one Python function. Vercel's CDN serves static/ directly;
vercel.json rewrites /api/*, /crew-sheet and /health here, and the app sees the original path."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402,F401
