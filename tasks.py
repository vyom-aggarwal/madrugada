"""Stdlib-only task runner mirroring the Makefile (for machines without make).

Usage: python tasks.py {setup|test|eval|demo|snapshot|demo_snapshot|real}
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
KEYS = ("CIMIS_APPKEY", "AIRNOW_KEY")


def run(*args: str) -> int:
    return subprocess.call(list(args), cwd=ROOT)


def setup() -> int:
    return run(PY, "-m", "pip", "install", "-r", "requirements.txt", "-r", "requirements-dev.txt")


def test() -> int:
    return run(PY, "-m", "pytest", "-x", "-q")


def eval_() -> int:
    script = ROOT / "eval" / "run_eval.py"
    if not script.exists():
        print("eval/run_eval.py not implemented yet")
        return 1
    return run(PY, str(script))


def snapshot() -> int:
    """Write static/snapshot.json (offline fallback for the UI)."""
    return run(PY, "-m", "app.snapshot")


def demo_snapshot() -> int:
    """Write the small committed static/demo_snapshot.json (24 real days selected for illustration)."""
    return run(PY, "-m", "app.snapshot", "demo")


def demo() -> int:
    """Fast, offline demo: serve the UI from committed results; no eval or full snapshot rebuild.
    Without a local real-data cache, the ?snapshot URL runs the UI from static/demo_snapshot.json."""
    has_real = any((ROOT / "data" / "cache").glob("real-*.json"))
    url = "http://127.0.0.1:8000/" + ("" if has_real else "static/index.html?snapshot")
    print(f"Madrugada demo: open {url}  (Ctrl+C to stop)", flush=True)
    return run(PY, "-m", "uvicorn", "app.main:app", "--port", "8000")


def real() -> int:
    """Fetch real days (CIMIS + AirNow if both keys are set, else keyless IEM ASOS + EPA AirData), then the
    preregistered eval + snapshot. See data/real_job.py."""
    missing = [k for k in KEYS if not os.environ.get(k)]
    print("real: " + (f"keys missing ({', '.join(missing)}); using the keyless path" if missing else "using CIMIS + AirNow"))
    return run(PY, "-m", "data.real_job")


TASKS = {"setup": setup, "test": test, "eval": eval_, "demo": demo, "snapshot": snapshot,
         "demo_snapshot": demo_snapshot, "real": real}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS:
        print(f"usage: python tasks.py {{{'|'.join(TASKS)}}}")
        sys.exit(2)
    sys.exit(TASKS[sys.argv[1]]())
