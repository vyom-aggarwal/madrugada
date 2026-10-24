"""Stdlib-only task runner mirroring the Makefile (for machines without make).

Usage: python tasks.py {setup|test|eval|demo}
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable


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


def demo() -> int:
    return run(PY, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000")


TASKS = {"setup": setup, "test": test, "eval": eval_, "demo": demo}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS:
        print(f"usage: python tasks.py {{{'|'.join(TASKS)}}}")
        sys.exit(2)
    sys.exit(TASKS[sys.argv[1]]())
