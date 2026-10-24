# Madrugada

**We tested whether shifting work hours reduces heat exposure for Central Valley farm crews.** It does only if
crews can start before dawn (04:00). At 05:30 or a sunrise-aligned start the benefit disappears. Smoke: a small
reduction vs the early fixed shift in window 2, none vs heat-only planning. So the tool's main output is the
**"Hours scheduling can't fix"** readout: the high-heat hours that remain in the best plan starting no earlier
than first light. Those hours need shade, rest or crew changes, not a different start time.

All results are modeled exposure-hours from airport weather (IEM ASOS) and nearby EPA monitors. Each window has
its own CI and they are never pooled. Numbers live in the result files, not in this README:
- Window 1, summers 2022 to 2025 (preregistered): `eval/results.md`
- Window 2, summers 2018 to 2021 (preregistered separately): `docs/results_w2.md`
- Start-time sensitivity (EXPLORATORY, POST-HOC): `docs/start_sensitivity.md`
- Pitch with every number filled from those files: `docs/PITCH_filled.md`

**It is not** a compliance tool, a health prediction, or a worker tracker. It does not replace the employer's
written Cal/OSHA Heat Illness Prevention Plan. Water, shade and rest requirements still apply.

## Run
```
python tasks.py setup          # install requirements (+ httpx for tests)
python tasks.py test           # pytest -x -q
python tasks.py demo           # fast, offline: serves committed results; prints the URL
python tasks.py real           # CIMIS + AirNow if both keys are set, else keyless IEM ASOS + EPA AirData
```
`python tasks.py eval`, `snapshot` (full, optional) and `demo_snapshot` rebuild those outputs. Without a local
real-data cache, `demo` prints a `?snapshot` URL that runs the UI from the committed `static/demo_snapshot.json`
(real days selected for illustration by a stated rule). Window 2 uses `analysis/fetch_window2.py` and
`analysis/eval_window2.py`. The real evals refuse to run unless the preregistration hashes match.

## Provenance rules
- Every day is `synthetic` or `real_cached`, shown as a badge; all days are replays ("REPLAY: recorded data, not live").
- Synthetic results are labeled "SYNTHETIC, NOT EVIDENCE" and never pooled with real days. Real windows are
  never pooled with each other. CIs resample whole dates, because region-days on a date are correlated.
- ORACLE mode plans on the day's own data and is labeled as an upper bound, not a forecast.
- Post-hoc analyses (`analysis/`) are labeled "EXPLORATORY, POST-HOC: not preregistered".

## Limitations
- The heat benefit assumes a 04:00 earliest start (a tunable assumption, not a legal limit).
- Airport air temperature, not field microclimate; no solar load. PM2.5 monitors are kilometres away (farthest
  in window 2), and some region-years had no monitor in range. Distances and exclusions are in the result files.
- Hourly PM2.5 is scored against 24-hour AQI breakpoints. The breakpoints are marked unverified in config; a later
  read-only check matched EPA's May 2026 document (`docs/verification_notes.md`).
- The forecast is a simple proxy (yesterday plus the 7-day mean). Cost weights are assumptions.
- First light uses approximate, unverified NOAA sunrise equations (sunrise minus 30 minutes).
- EPA AirData release status (preliminary or certified) is unverifiable. PurpleAir is not used.
- No worker input was modeled. The Spanish text needs a native-speaker review.
