# Pre-registration: Madrugada real-data evaluation

Date: 2026-10-24. Written and committed BEFORE the first real-data eval.

## Data

- Regions: bakersfield (Bakersfield, ASOS KBFL), fresno (Fresno, ASOS KFAT), tulare (Tulare/Visalia, ASOS KVIS).
- Window: 06-01 to 09-30 of 2022, 2023, 2024, 2025; plus the 14 days before each season start as forecast history only (evaluated if they have their own 7-day history, like every other day).
- Sources: CIMIS + AirNow if both keys are set, otherwise IEM ASOS (temperature, RH) + EPA AirData hourly PM2.5 (88101; nearest active monitor within 25 km of the ASOS station).
- Usable day: >= 90% of 15-minute slots observed for BOTH temperature and PM2.5 after linear interpolation of gaps up to 2 h. Years whose AirData file is missing or incomplete are excluded. All usable days are evaluated; none are selected after seeing results.

## Rules

- Strata on observed data: heat = max temp >= 95F, smoke = max AQI >= 101; heat_only, smoke_only, co_occurring (both), mild (neither).
- PRIMARY outcome: physical dominance (win = no more hours >=95F and no more AQI>=101 hours, strictly less on one; loss = reverse; tie = all physical metrics within 0.125 h; else mixed). Cost-based outcomes are secondary ("uses the optimizer's own cost").
- Comparisons: optimizer, robust, oracle (upper bound) against B1, B2, b3_early, b3_late, by stratum and overall. Robust only on days without fallback, and against the optimizer on those same days.
- CIs: cluster bootstrap over calendar dates (seed 20250801, 10000 resamples), skipped for groups with fewer than 10 dates. Region-days are not the effective sample size.
- Weight sensitivity: w_heat [0.5, 1, 2], w_smoke [0.5, 1, 2], w_dual [0, 1, 2], cost levels [[0, 1, 3], [0, 1, 2], [0, 1, 5]]; headline day-level.
- Forecast-proxy sensitivity: ['prev_day_only', 'mean_7day_only'] and the default blend.
- Secondary: NowCast-based hours at AQI>=101 and >=151 (observed only; planning unchanged).
- Minimum real days for any real-data conclusion: 20. Real and synthetic days never pooled.

## Hashes (SHA-256)

Config hash excludes the non-logic keys: real_data.cimis.url, real_data.airnow.url, real_job.cimis_station_list_url, real_job.throttle, keyless.iem.url, keyless.airdata.url_template, keyless.airdata.listing_url.
Documented non-logic files (not hashed): eval/report.py, eval/inventory.py, eval/fixture_table.py, app/main.py, app/planning.py, app/snapshot.py, app/crew_sheet.py, static/*, docs/*, README.md, tests/*, tasks.py, data/real_job.py, data/keyed.py, data/fetcher.py, CLAUDE.md.

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
