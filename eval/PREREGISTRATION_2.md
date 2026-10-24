# Pre-registration 2: Madrugada WINDOW 2 (summers 2018 to 2021)

Date: 2026-10-24. Written and committed BEFORE fetching or evaluating any window-2 data. Window-1 results (eval/results.json, summers 2022 to 2025) were already known when this was written; window 2 is an out-of-sample replication with the frozen code and rules.

## Data

- Window: 06-01 to 09-30 of 2018, 2019, 2020, 2021, plus the 14 days before each June 1 as history (evaluated only if they have their own 7-day history, exactly as in window 1).
- Regions and sources (keyless, same as window 1): bakersfield (ASOS KBFL), fresno (ASOS KFAT), tulare (ASOS KVIS); IEM ASOS temperature/RH and EPA AirData hourly PM2.5 (88101), nearest active monitor within 25 km.
- Separate cache: data/cache_w2/ (window 1's data/cache/ is never written). Fetched one year at a time with the frozen keyless job; a year whose AirData or IEM files are unavailable or incomplete is excluded and reported.
- Usability: >= 90% of slots observed for both temperature and PM2.5 after interpolating gaps up to 2 h. Forecast proxy, strata rule ({'heat_temp_f': 95, 'smoke_aqi': 101}) and all other rules unchanged.

## Analysis

- Same functions as window 1 (eval/run_eval.run on the window-2 pool), called by analysis/eval_window2.py, which refuses to run unless these hashes match.
- PRIMARY outcome: physical dominance (no more hours >=95F and no more AQI>=101 hours, strictly less on one). Comparisons: optimizer, robust (non-fallback days; and vs the optimizer on the same days) and oracle against B1, B2, b3_early, b3_late, by stratum and overall. Cost outcomes secondary.
- CIs: date-cluster bootstrap (seed 20250801, 10000 resamples), none for groups with fewer than 10 dates. Weight and forecast-proxy sensitivity as in window 1.
- Minimum 20 real days. Window-2 results are reported separately and NEVER pooled with window 1 in any confirmatory statement; a pooled table may appear only if labeled exploratory.
- The start-time sensitivity repeated on window 2 is EXPLORATORY, POST-HOC (it was designed after window 1).

## Hashes (SHA-256): must equal eval/PREREGISTRATION.md

Same non-logic exclusions as eval/PREREGISTRATION.md; analysis/ files are non-logic.

- `37d10744117567ba4436d23d0069bc7345ce94b1a3e10559b20e0416e01746fd` app/aqi.py
- `b8e949bfb18d9b3cf714ee8cd58a046e75a449863617e44e5be0f482f4bac9c8` app/baselines.py
- `a6990336ff0ab59ce64c14e52204340df02dedbbf1cce62b409ade5574d6bc98` app/config.py
- `96babd59f5bfb1045c5f5875b20a3fd243775ccdd0719da07ce1c519e11f3365` app/exposure.py
- `51a95ba3789d22f8c48a46aa0797376922493daed93facbc0d2907e0727f8259` app/forecast.py
- `bc93fcd7be9cde8eb5dab042a1812c6a55950c85b30d58ae5012e93a860d5f18` app/models.py
- `1484e944a7e4a40d794faf5ab961e7556a1e5d7c049303f1ac2b7f2ec83b3b0d` app/optimizer.py
- `fe75b24bdfc89291fb8414f1cfbe4caa110b77a8926e5b55a28d903685a80e6c` app/robust.py
- `5691fd14720a5f94334e014dff01c17f4c9f4c52f8be5f53688bdfc720ccd973` eval/metrics.py
- `6d14a4c3e6062cc7f56dec1ec670076e77b0dbe248e0a1a5b1469b1981e1aa94` eval/prereg.py
- `1e192409e9149ea45a59f6089966c4ca3d6cfc700593dedef57462ec2e5a54ce` eval/run_eval.py
- `b2faab623901be308146dbc0371b123713e3eaf4bc2ac3b63b84b45ad89f4f72` eval/stats.py
- `bc02bebac8c00bbd5bd14f0940a49db177d7469be06c12a53e3479ca617f10e2` data/fetch_real.py
- `270344261efdd1ef5efddf97ccdabf2b21debab6f48cdcb88e7df4b8503125ba` data/keyless.py
- `f65b6ae2cec0d728970b08fcb02f376618621efebe192439cee3c943d7ed5c3e` data/keyless_job.py
- `0f588f0127933cbebdc64cf422bdcd73a34c0adb9165b64b440bc407dbe930f4` data/real_checks.py
- `ab0ca5af4a9e24de4fbfaae83dc7ba2538dcca3de774b856300c3830dd8d1e98` config.yaml#logic
