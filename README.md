# Madrugada

A heat + wildfire-smoke shift planner for Central Valley farm crews. Given hourly temperature and PM2.5,
it recommends one or two work blocks that keep paid hours constant while reducing **modeled
exposure-hours** (hours >=80F / >=95F, AQI >=101 / >=151, and both at once), and compares that plan
with fixed shifts (B1 07:00-15:30, B2 05:30-14:00) and a heat-only planner (B3).

**It is not** a compliance tool, a health prediction, or a worker tracker. It does not replace the
employer's written Cal/OSHA Heat Illness Prevention Plan. Water, shade and rest requirements still apply.

## Run
```
python tasks.py setup      # install requirements (+ httpx for tests)
python tasks.py test       # pytest -x -q
python tasks.py demo       # eval -> snapshot -> server at http://127.0.0.1:8000/
python tasks.py real       # real CIMIS + AirNow job; needs CIMIS_APPKEY and AIRNOW_KEY
```
`python tasks.py eval` and `python tasks.py snapshot` run those steps alone. If an API call fails in
the browser, the page falls back to `static/snapshot.json` ("SNAPSHOT MODE: sliders disabled").

## Provenance rules
- Every day is `synthetic` or `real_cached`, shown as a badge on every view. All days are replays
  ("REPLAY: recorded data, not live").
- Synthetic results are always labeled "SYNTHETIC, NOT EVIDENCE" and never pooled with real days.
- Real-data conclusions need at least 20 real days; otherwise the outputs say "insufficient real days".
- ORACLE mode plans on the day's own data and is labeled as an upper bound, not a forecast.

## Limitations
- Station-level data, not field microclimate. Direct sun load adds heat that air temperature misses.
- Outputs are modeled exposure-hours only, not health outcomes.
- The forecast is a simple proxy: 0.5 x yesterday + 0.5 x the mean of the prior 7 days.
- The PurpleAir PM2.5 correction underestimates above about 250 ug/m3. PurpleAir is not used in the evaluation.
- Cost weights and levels are assumptions; see the weight-sensitivity table.
- Spanish text needs native-speaker review.
- PM2.5->AQI breakpoints, CIMIS/AirNow endpoints, fields, units and time conventions are unverified
  (see config.yaml and, after a real run, docs/real_data_notes.md).

## 100-second demo script
1. `python tasks.py demo`, open the URL. Point at the provenance and REPLAY badges.
2. Day selector: pick a co-occurring day. Show the temperature and AQI panels, the dashed threshold
   lines, the shaded recommended blocks, and the B1/B2 bars beneath.
3. Comparison table: read the optimizer, B2 and both B3 rows. Toggle "observed (what happened)".
4. Move the paid-hours slider; click a Pareto point to load that trade-off into the chart.
5. Tick ORACLE and note the "upper bound, not a forecast" badge. Untick it.
6. Backtest: read the first line (provenance statement) and the "What this does and does not show"
   box aloud, including whatever it says about B3.
7. Read the PRIMARY physical-dominance row "optimizer vs B2" (overall) and the "optimizer vs b3_early"
   row, then the day-level weight-sensitivity headline. Quote the numbers on screen; do not round up.
8. Read the oracle diagnosis sentence.
9. Click "Print crew sheet": show the 12-hour blocks, bilingual summary and disclaimer.
10. Close on the footer: advisory aid, modeled exposure-hours only.
