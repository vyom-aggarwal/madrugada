# Madrugada: dual-hazard (heat + smoke) shift planner for Central Valley farm crews

## Purpose
Given hourly temperature and PM2.5 for a field, recommend a crew shift that keeps paid hours
roughly constant while minimizing hours worked in the worst heat and smoke. Hackathon MVP.
Advisory tool only. It does not certify Cal/OSHA compliance and does not track individual workers.

## Hard rules
1. NEVER present synthetic or replayed data as a real measurement. Every dataset carries a
   `provenance` field ("real_cached" | "synthetic") and the UI/eval output must display it.
2. No ML models. The value is the optimizer, the sensor correction, and the evaluation.
3. No new heavy dependencies. Allowed: fastapi, uvicorn, pydantic, numpy, pandas, pytest, pyyaml,
   requests, httpx (dev/test only, in requirements-dev.txt, never imported by app code).
   Frontend is ONE static index.html (vanilla JS) plus a vendored chart lib in /static.
   No npm, no build step, no CDN at runtime (must work offline).
4. Thresholds come from `config.yaml` only (never hardcode):
   - heat: 80F (Cal/OSHA shade trigger), 95F (Cal/OSHA high-heat procedures)
   - smoke: AQI 101 and 151 (151 = Cal/OSHA wildfire smoke rule trigger)
   - dual-hazard (our own tunable definition): temp >= 90F AND AQI >= 101
   - Add a comment in config.yaml: "Verify PM2.5->AQI breakpoints against current EPA table."
5. Report exposure-hours only. Never claim lives saved or health outcomes.
6. Keep files small. Prefer one module per concern. Max ~200 lines per file.

## Layout
madrugada/
  config.yaml
  app/ {main.py, models.py, exposure.py, optimizer.py, baselines.py, aqi.py, forecast.py}
  data/ {fixtures/, cache/, make_fixtures.py, fetch_real.py}
  eval/ {days.yaml, run_eval.py, results.json, results.md}
  static/ {index.html, chart.min.js}
  tests/
  Makefile   (targets: setup, test, eval, demo)

## Domain spec
- Time grid: 15-minute slots, 96 per day.
- Day record: {id, label, region, provenance, temp_f[96], rh[96], solar_wm2[96], pm25_ugm3[96]}
- Shift: up to 2 work blocks. Inputs: paid_hours_target, earliest_start, latest_end, min_block_hours (2),
  min_gap_hours (1). Paid hours = total work time; breaks are not paid-hours constraints in the MVP.
- Cost per slot = w_heat * heat_cost(T) + w_smoke * smoke_cost(AQI) + w_dual * dual_flag.
  heat_cost: 0 below 80F, 1 for 80-95F, 3 at or above 95F. smoke_cost: 0 below AQI 101, 1 for 101-150, 3 at or above 151.
  All weights and levels in config.yaml.
- Optimizer: exhaustive search over block start/end on the grid (numpy, prefix sums). No solver needed.
- Pareto: sweep paid_hours_target (100% down to 80% of requested) and heat/smoke weight ratio.
  Return non-dominated points on (heat_hours, smoke_hours, paid_hours).
- Baselines: B1 fixed 07:00-15:30. B2 fixed early start 05:30-14:00. B3 heat-only optimizer (w_smoke=0).
- PM2.5 sensor correction (PurpleAir): EPA US-wide formula 0.524*pm_cf1 - 0.0862*RH + 5.75 (verify
  against Barkjohn et al. 2021). Known limit: underestimates above ~250 ug/m3; surface this as a warning.
- Forecast proxy (leakage-safe): plan for day D uses ONLY data from day D-1 and earlier:
  0.5 * (D-1 profile) + 0.5 * (mean profile of prior 7 days). Also support `oracle=true` (uses day D truth)
  as an upper bound, labeled "ORACLE" everywhere.
- Evaluation: score every plan against day D observed values. Metrics: hours >=95F, hours >=80F,
  hours AQI>=101, hours AQI>=151, dual-hazard hours, paid hours retained.
- Crew sheet: printable bilingual (EN/ES) HTML page. Add a note: "Spanish text needs native-speaker review."

## Working style (usage limits)
- Do only the phase requested. Do not refactor earlier phases.
- Don't re-read files you just wrote. Don't explore the repo broadly.
- Run tests with `pytest -x -q`. Never loop on a failing test more than 3 attempts, then report.
- After each phase: run tests, commit with message "phase N: <summary>", and print a status of 10 lines max.
- No web browsing, no downloading datasets inside a phase unless the phase says so.

## Phase 2 decisions
- DayRecord slots are LOCAL CLOCK TIME (America/Los_Angeles, including daylight time). Every real-data
  adapter must convert to this before writing. (zoneinfo needs `tzdata` on Windows; it is a pandas
  dependency and is listed in requirements.txt.)
- Default paid_hours_target = 8.5, equal to the B1 and B2 baseline shift lengths, so comparisons are like
  for like. The Pareto sweep may go down to 80% of the request.
- Default earliest_start 04:00 and latest_end 19:00 (config.yaml). These are tunable assumptions, not legal limits.
- Fixtures and any replayed data are illustrations. Only the real-data backtest counts as evidence for the
  dual-hazard claim. Never tune fixtures or weights to make a test pass.