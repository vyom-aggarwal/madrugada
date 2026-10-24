EXPLORATORY, POST-HOC: NOT PREREGISTERED. SUMMER 2022 TO 2025, AIRPORT WEATHER AND NEARBY EPA MONITORS, MODELED EXPOSURE-HOURS ONLY.

# Exploratory findings (real data)

_EXPLORATORY, POST-HOC: not preregistered._

1296 real region-days on 509 dates (the preregistered evaluation set). Strata use the frozen rule. Differences are optimizer minus baseline; CIs are date-cluster bootstrap (frozen seed, 10,000 resamples), skipped for groups with fewer than 10 dates.

## 1. Strata inventory

_EXPLORATORY, POST-HOC: not preregistered._

| stratum | region-days | dates |
|---|---|---|
| heat_only | 630 | 296 |
| smoke_only | 38 | 30 |
| co_occurring | 71 | 60 |
| mild | 557 | 236 |

| region | heat_only | smoke_only | co_occurring | mild |
|---|---|---|---|---|
| bakersfield | 176 | 18 | 37 | 184 |
| fresno | 249 | 5 | 7 | 201 |
| tulare | 205 | 15 | 27 | 172 |

| year | heat_only | smoke_only | co_occurring | mild |
|---|---|---|---|---|
| 2022 | 157 | 14 | 13 | 112 |
| 2023 | 118 | 10 | 15 | 193 |
| 2024 | 193 | 2 | 27 | 120 |
| 2025 | 162 | 12 | 16 | 132 |

Days with any observed AQI>=101 hour: 109 (187 h total); any AQI>=151 hour: 29 (41 h total).

## 2. Effect by stratum (mean difference [95% CI])

_EXPLORATORY, POST-HOC: not preregistered._

| comparison | stratum | n | dates | h >=95F | h >=80F | h AQI>=101 |
|---|---|---|---|---|---|---|
| optimizer vs B2 | overall | 1296 | 509 | -0.377 [-0.427, -0.328] | -1.215 [-1.260, -1.167] | -0.001 [-0.007, +0.005] |
| optimizer vs B2 | heat_only | 630 | 296 | -0.661 [-0.736, -0.589] | -1.366 [-1.401, -1.327] | +0.000 [+0.000, +0.000] |
| optimizer vs B2 | smoke_only | 38 | 30 | +0.000 [+0.000, +0.000] | -1.007 [-1.220, -0.764] | +0.092 [+0.000, +0.208] |
| optimizer vs B2 | co_occurring | 71 | 60 | -1.014 [-1.157, -0.860] | -1.148 [-1.288, -1.007] | -0.063 [-0.162, +0.029] |
| optimizer vs B2 | mild | 557 | 236 | +0.000 [+0.000, +0.000] | -1.067 [-1.153, -0.977] | +0.000 [+0.000, +0.000] |
| optimizer vs b3_late | overall | 1296 | 509 | +0.002 [-0.001, +0.005] | -0.079 [-0.116, -0.048] | +0.001 [+0.000, +0.002] |
| optimizer vs b3_late | heat_only | 630 | 296 | +0.004 [-0.000, +0.011] | +0.003 [-0.004, +0.012] | +0.000 [+0.000, +0.000] |
| optimizer vs b3_late | smoke_only | 38 | 30 | +0.000 [+0.000, +0.000] | -0.165 [-0.408, -0.007] | +0.026 [+0.000, +0.081] |
| optimizer vs b3_late | co_occurring | 71 | 60 | -0.007 [-0.022, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| optimizer vs b3_late | mild | 557 | 236 | +0.000 [+0.000, +0.000] | -0.176 [-0.251, -0.112] | +0.000 [+0.000, +0.000] |

## 3. Anatomy of 'mixed' days vs B2

_EXPLORATORY, POST-HOC: not preregistered._

| stratum | mixed | heat down, smoke up | heat up, smoke down | 95F & AQI101 unchanged | heat-down side: -h95 median/p90 | smoke-up side: +h101 median/p90 | unchanged: h80 change median |
|---|---|---|---|---|---|---|---|
| overall | 751 | 4 | 0 | 747 | 1.5/1.5 | 0.5/0.5 | -1.5 |
| heat_only | 279 | 0 | 0 | 279 | None/None | None/None | -1.5 |
| smoke_only | 28 | 0 | 0 | 28 | None/None | None/None | -1.5 |
| co_occurring | 13 | 4 | 0 | 9 | 1.5/1.5 | 0.5/0.5 | -1.5 |
| mild | 431 | 0 | 0 | 431 | None/None | None/None | -1.5 |

## 4. Smoke movability (days with >= 1 observed AQI>=101 hour)

_EXPLORATORY, POST-HOC: not preregistered._

- Smoke days: 109.
- Oracle vs B2, AQI>=101 hours removed: total 33.25, mean 0.305, median 0.0; days with any removed: 26.
- Oracle vs B2, change in hours >=95F on the same days: total -61.75, mean -0.567 (negative = fewer heat hours).
- AQI>=101 hours inside the heat-optimal window (heat-only optimizer on observed data): 82 h; outside it but within the allowed 04:00-19:00 window: 32 h; outside the allowed window: 73 h.
- Smoke days by where their in-window smoke hours fall: {'none in shift hours': 38, 'all inside': 45, 'all outside': 14, 'split': 12}.

## 5. Time of day: mean observed AQI and temperature by local clock hour

_EXPLORATORY, POST-HOC: not preregistered._

**overall** (n=1296): cleanest hours [17, 18, 16], dirtiest [9, 8, 10], coolest [6, 5, 7], hottest [17, 16, 18].

| hour | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AQI | 47.2 | 48.3 | 46.0 | 45.0 | 45.5 | 46.7 | 49.2 | 51.3 | 52.0 | 52.6 | 51.7 | 50.3 | 48.5 | 46.6 | 45.2 | 43.8 | 43.1 | 42.6 | 42.9 | 44.6 | 47.4 | 49.4 | 49.1 | 48.2 |
| temp F | 76.5 | 74.5 | 72.6 | 70.9 | 69.5 | 68.3 | 67.6 | 68.9 | 72.3 | 76.1 | 79.8 | 83.3 | 86.6 | 89.4 | 91.6 | 93.3 | 94.3 | 94.4 | 93.5 | 91.1 | 87.2 | 83.8 | 81.3 | 78.8 |

**heat_only** (n=630): cleanest hours [18, 17, 16], dirtiest [9, 8, 10], coolest [6, 5, 7], hottest [17, 16, 18].

| hour | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AQI | 49.8 | 50.7 | 49.2 | 48.0 | 49.2 | 50.4 | 53.0 | 55.5 | 55.7 | 56.7 | 55.6 | 53.7 | 52.1 | 50.3 | 49.1 | 46.9 | 45.2 | 44.7 | 44.4 | 46.1 | 49.0 | 50.3 | 49.8 | 49.0 |
| temp F | 80.5 | 78.3 | 76.3 | 74.6 | 73.0 | 71.7 | 71.0 | 72.5 | 76.2 | 80.4 | 84.3 | 88.1 | 91.6 | 94.6 | 97.0 | 98.8 | 99.8 | 100.0 | 99.1 | 96.5 | 92.2 | 88.3 | 85.5 | 82.9 |

**smoke_only** (n=38): cleanest hours [18, 17, 19], dirtiest [22, 21, 23], coolest [6, 5, 7], hottest [16, 17, 15].

| hour | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AQI | 64.5 | 67.8 | 54.6 | 54.9 | 55.7 | 54.8 | 61.4 | 60.7 | 65.4 | 63.3 | 64.2 | 57.3 | 54.3 | 52.5 | 54.1 | 57.2 | 55.9 | 51.9 | 50.8 | 51.9 | 55.9 | 76.5 | 78.0 | 68.1 |
| temp F | 71.8 | 70.0 | 68.3 | 67.0 | 65.7 | 64.4 | 63.7 | 64.7 | 67.5 | 70.8 | 74.0 | 77.1 | 80.2 | 82.9 | 85.0 | 86.6 | 87.5 | 87.4 | 86.5 | 84.2 | 81.2 | 78.6 | 76.5 | 74.2 |

**co_occurring** (n=71): cleanest hours [16, 17, 15], dirtiest [8, 6, 7], coolest [6, 5, 4], hottest [16, 17, 15].

| hour | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AQI | 61.6 | 63.9 | 62.0 | 60.3 | 61.7 | 68.1 | 74.8 | 71.4 | 76.7 | 70.9 | 66.0 | 69.5 | 64.6 | 62.3 | 58.0 | 55.9 | 53.4 | 53.8 | 58.8 | 58.2 | 62.0 | 68.5 | 69.0 | 64.9 |
| temp F | 82.4 | 80.5 | 78.6 | 76.8 | 75.1 | 74.1 | 73.6 | 75.3 | 79.3 | 83.2 | 87.0 | 90.7 | 94.1 | 97.1 | 99.5 | 101.1 | 102.3 | 102.2 | 101.0 | 98.0 | 93.3 | 89.3 | 86.7 | 84.2 |

**mild** (n=557): cleanest hours [15, 17, 16], dirtiest [9, 10, 21], coolest [6, 5, 7], hottest [17, 16, 18].

| hour | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AQI | 41.2 | 42.3 | 39.7 | 39.0 | 38.6 | 39.2 | 40.9 | 43.3 | 43.8 | 45.0 | 44.7 | 43.4 | 42.0 | 40.0 | 38.6 | 37.8 | 38.5 | 38.1 | 38.7 | 40.6 | 43.0 | 44.2 | 43.7 | 43.7 |
| temp F | 71.6 | 69.6 | 67.9 | 66.4 | 65.1 | 64.0 | 63.3 | 64.4 | 67.3 | 70.7 | 74.1 | 77.4 | 80.4 | 82.9 | 85.0 | 86.5 | 87.5 | 87.6 | 86.7 | 84.5 | 81.3 | 78.4 | 76.1 | 73.8 |

## What this does and does not support

Supports:

- Heat: vs B2 the optimizer has -0.38 h/day at >=95F (CI [-0.4268, -0.3275]) and -1.22 h/day at >=80F (CI [-1.2603, -1.1671]).
- Mixed days vs B2 are mostly not heat-for-smoke trade-offs: 747 of 751 have identical >=95F and AQI>=101 hours and differ in another metric (median change in >=80F hours -1.5); 4 are trade-offs.

Does not support:

- A smoke benefit: AQI>=101 difference vs B2 is -0.0008 h/day (CI [-0.007, 0.0053]).
- Smoke was rare: 109 of 1296 region-days had any AQI>=101 hour (187 h in total) and 29 had any AQI>=151 hour (41 h). Smoke-only and co-occurring strata have 30 and 60 dates.
- Smoke is hard to move even with perfect knowledge: on the 109 days with >=1 AQI>=101 hour the oracle removes 33.25 smoke hours vs B2 in total (mean 0.305 h/day, median 0.0).
- Time of day: mean AQI is lowest at hours [17, 18, 16] and highest at [9, 8, 10]; temperature is lowest at [6, 5, 7] and highest at [17, 16, 18]. The cleanest hours do not coincide with the coolest hours.
- Any field-level, health or compliance claim: airport temperature and monitors several km away; modeled exposure-hours only.
