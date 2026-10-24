"""Stdlib-only task runner mirroring the Makefile (for machines without make).

Usage: python tasks.py {setup|test|eval|demo|snapshot|real}
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


def demo() -> int:
    """Run the eval, build the snapshot, then serve the UI."""
    for step in (eval_, snapshot):
        rc = step()
        if rc:
            return rc
    print("Madrugada demo: open http://127.0.0.1:8000/  (Ctrl+C to stop)", flush=True)
    return run(PY, "-m", "uvicorn", "app.main:app", "--port", "8000")


def real() -> int:
    """Fetch real days (CIMIS + AirNow if both keys are set, else keyless IEM ASOS + EPA AirData), then the
    preregistered eval + snapshot. See data/real_job.py."""
    missing = [k for k in KEYS if not os.environ.get(k)]
    print("real: " + (f"keys missing ({', '.join(missing)}); using the keyless path" if missing else "using CIMIS + AirNow"))
    return run(PY, "-m", "data.real_job")


TASKS = {"setup": setup, "test": test, "eval": eval_, "demo": demo, "snapshot": snapshot, "real": real}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS:
        print(f"usage: python tasks.py {{{'|'.join(TASKS)}}}")
        sys.exit(2)
    sys.exit(TASKS[sys.argv[1]]())
