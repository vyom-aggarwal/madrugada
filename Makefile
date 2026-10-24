# Same targets as tasks.py (use `python tasks.py <target>` where make is unavailable).
PY ?= python

.PHONY: setup test eval demo

setup:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest -x -q

eval:
	$(PY) eval/run_eval.py

demo:
	$(PY) -m uvicorn app.main:app --reload --port 8000
