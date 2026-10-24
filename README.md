# Madrugada

A **heat-first shift planner with smoke exposure shown**, for Central Valley farm crews. From hourly
temperature and PM2.5 it recommends one or two work blocks that keep paid hours constant while reducing
**modeled heat exposure-hours**, and shows smoke (AQI) exposure next to every plan. It compares the plan with
fixed shifts (B1 07:00-15:30, B2 05:30-14:00) and a heat-only planner (B3).

**Real-data results** (airport weather and nearby EPA monitors; modeled exposure-hours only):
- Window 1 (summers 2022 to 2025, `eval/results.md`) and window 2 (summers 2018 to 2021, `docs/results_w2.md`)
  were each preregistered before their data were evaluated, and are never pooled. Both show fewer hours at >=95F
  than the fixed 05:30 shift, and nearly always the same plan as heat-only planning. Smoke: window 1 shows no
  measurable change vs the fixed shift. Window 2 (smokier years) shows a small AQI>=101 reduction vs the fixed
  shift but none vs heat-only planning. Only the robust variant shows a small one vs heat-only, at a small heat cost.
- That heat benefit comes from the assumed **04:00 earliest start**, not from the planning. At 05:30 or a
  sunrise-based earliest start it disappears, and a fixed shift at the earliest allowed time does as well
  (`docs/start_sensitivity.md`, EXPLORATORY, POST-HOC). It does **not** beat heat-only planning on smoke.

**It is not** a compliance tool, a health prediction, or a worker tracker. It does not replace the
employer's written Cal/OSHA Heat Illness Prevention Plan. Water, shade and rest requirements still apply.

## Run
```
python tasks.py setup          # install requirements (+ httpx for tests)
python tasks.py test           # pytest -x -q
python tasks.py demo           # fast, offline: serves committed results; prints the URL
python tasks.py real           # CIMIS + AirNow if both keys are set, else keyless IEM ASOS + EPA AirData
```
`python tasks.py eval`, `python tasks.py snapshot` (full, optional) and `python tasks.py demo_snapshot` rebuild
those outputs. Without a local real-data cache, `demo` prints a `?snapshot` URL that runs the UI from the
committed `static/demo_snapshot.json` (24 real days selected for illustration by a stated rule). The real eval
runs only if the `eval/PREREGISTRATION.md` hashes match the code and config.

## Provenance rules
- Every day is `synthetic` or `real_cached`, shown as a badge. All days are replays ("REPLAY: recorded data, not live").
- Synthetic results are labeled "SYNTHETIC, NOT EVIDENCE" and never pooled with real days. Real-data
  conclusions need at least 20 real days. CIs resample whole dates, because region-days on a date are correlated.
- ORACLE mode plans on the day's own data and is labeled as an upper bound, not a forecast.
- Post-hoc analyses (`analysis/`) are labeled "EXPLORATORY, POST-HOC: not preregistered".

## Limitations
- The heat benefit assumes a 04:00 earliest start (a tunable assumption, not a legal limit).
- Airport (ASOS) air temperature, not field microclimate; no solar load. PM2.5 monitors are several km away
  (up to 22 km in window 2). Hourly PM2.5 is scored against 24-hour AQI breakpoints.
- Outputs are modeled exposure-hours only, not health outcomes.
- The forecast is a simple proxy (0.5 x yesterday + 0.5 x the prior 7-day mean). Cost weights are assumptions.
- Smoke was rare in the window, and the cleanest hours are late afternoon, when it is hottest.
- EPA AirData release status (preliminary or certified) is unverifiable from the listing. PurpleAir is not used.
- The robust planner fell back on days without enough history. No worker input was modeled.
- Spanish text needs native-speaker review.
- PM2.5 AQI breakpoints and NowCast matched EPA's May 2026 document (`docs/verification_notes.md`).
  CIMIS/AirNow conventions are unverified (no keys).

## Demo and pitch
The 100-second demo script, the claims table and judge Q&A are in `docs/PITCH.md`. Numbers are filled from
the results by `python -m analysis.fill_pitch` into `docs/PITCH_filled.md`.
