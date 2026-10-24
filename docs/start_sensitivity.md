EXPLORATORY, POST-HOC: NOT PREREGISTERED

# Start-time sensitivity (window 1, summers 2022 to 2025)

1296 real region-days on 509 dates. Paid hours 8.5, latest end, min block and min gap as in config. B_sun = a fixed 8.5 h shift starting at the setting's earliest start. The sunrise rule uses approximate, unverified NOAA equations (sunrise minus 30 min, rounded to 15 min); station coordinates: {'bakersfield': [35.4344, -119.0542, 'manifest'], 'fresno': [36.78, -119.7194, 'manifest'], 'tulare': [36.3187, -119.3929, 'manifest']}. CIs are date-cluster bootstrap (frozen seed, 10,000 resamples).

## What this shows

- At earliest start 05:30, the optimizer vs B2 has +0.004 [+0.001, +0.008] h/day at >=95F, about +0.2 min/day (clearly MORE hours); none of the 04:00 benefit (-0.377 h/day) remains.
- At earliest start sunrise, the optimizer vs B2 has +0.027 [+0.012, +0.042] h/day at >=95F, about +1.6 min/day (clearly MORE hours); none of the 04:00 benefit (-0.377 h/day) remains.
- 04:00: one block placed by the optimizer vs B2 -0.379 [-0.429, -0.329]; adding a second block (two-block vs one-block) +0.002 [+0.000, +0.005]. Two-block plans chosen on 0.5% of days.
- 05:30: one block placed by the optimizer vs B2 +0.000 [+0.000, +0.000]; adding a second block (two-block vs one-block) +0.004 [+0.001, +0.008]. Two-block plans chosen on 0.9% of days.
- sunrise: one block placed by the optimizer vs B2 +0.023 [+0.009, +0.037]; adding a second block (two-block vs one-block) +0.004 [+0.001, +0.007]. Two-block plans chosen on 1.6% of days.
- Against B_sun (a fixed shift at the same earliest start) the optimizer has +0.002 [+0.000, +0.005] at 04:00, physical W/T/L/M 0/1290/3/3: the heat benefit vs B2 comes from starting at the earliest allowed time, not from splitting the shift or from the forecast.

## Hours >=95F, mean difference per day [95% CI], overall

| earliest | opt vs B2 | opt vs B_sun | oracle vs B2 | oracle vs B_sun | 1-block vs B2 | 2-block vs 1-block | two-block share | median gap h | mean h95 B2 / B_sun / opt |
|---|---|---|---|---|---|---|---|---|---|
| 04:00 | -0.377 [-0.427, -0.328] | +0.002 [+0.000, +0.005] | -0.373 [-0.423, -0.323] | +0.007 [+0.001, +0.014] | -0.379 [-0.429, -0.329] | +0.002 [+0.000, +0.005] | 0.5% | 2.75 | 0.5434 / 0.1642 / 0.1665 |
| 04:30 | -0.278 [-0.314, -0.242] | +0.004 [+0.001, +0.008] | -0.275 [-0.311, -0.239] | +0.007 [-0.000, +0.015] | -0.282 [-0.318, -0.246] | +0.004 [+0.001, +0.008] | 0.8% | 2.75 | 0.5434 / 0.2614 / 0.2654 |
| 05:00 | -0.150 [-0.169, -0.131] | +0.004 [+0.001, +0.007] | -0.147 [-0.167, -0.126] | +0.007 [-0.002, +0.016] | -0.153 [-0.172, -0.135] | +0.004 [+0.001, +0.007] | 0.8% | 3.5 | 0.5434 / 0.3899 / 0.3937 |
| 05:30 | +0.004 [+0.001, +0.008] | +0.004 [+0.001, +0.008] | +0.006 [-0.003, +0.016] | +0.006 [-0.003, +0.016] | +0.000 [+0.000, +0.000] | +0.004 [+0.001, +0.008] | 0.9% | 4.5 | 0.5434 / 0.5434 / 0.5473 |
| 06:00 | +0.185 [+0.165, +0.205] | +0.003 [+0.001, +0.006] | +0.186 [+0.163, +0.208] | +0.003 [-0.006, +0.014] | +0.182 [+0.162, +0.202] | +0.003 [+0.001, +0.006] | 1.2% | 4.5 | 0.5434 / 0.7259 / 0.7288 |
| sunrise | +0.027 [+0.012, +0.042] | +0.004 [+0.001, +0.007] | +0.027 [+0.009, +0.044] | +0.004 [-0.005, +0.013] | +0.023 [+0.009, +0.037] | +0.004 [+0.001, +0.007] | 1.6% | 4.25 | 0.5434 / 0.5664 / 0.5702 |

## Physical dominance W/T/L/mixed and other metrics, overall

| earliest | opt vs B2 | opt vs B_sun | oracle vs B2 | h>=80F opt vs B2 | AQI>=101 opt vs B2 |
|---|---|---|---|---|---|
| 04:00 | 405/135/5/751 | 0/1290/3/3 | 413/134/2/747 | -1.215 [-1.260, -1.167] | -0.001 [-0.007, +0.005] |
| 04:30 | 401/138/7/750 | 0/1287/5/4 | 412/134/2/748 | -0.823 [-0.854, -0.790] | +0.001 [-0.004, +0.005] |
| 05:00 | 401/135/9/751 | 0/1288/5/3 | 405/134/2/755 | -0.417 [-0.434, -0.398] | +0.001 [-0.002, +0.004] |
| 05:30 | 0/1288/5/3 | 0/1288/5/3 | 13/1263/0/20 | +0.007 [+0.000, +0.021] | +0.000 [+0.000, +0.000] |
| 06:00 | 3/97/482/714 | 0/1287/5/4 | 11/102/455/728 | +0.448 [+0.432, +0.464] | -0.002 [-0.004, +0.001] |
| sunrise | 166/291/193/646 | 0/1284/5/7 | 176/293/177/650 | +0.103 [+0.070, +0.137] | -0.001 [-0.003, +0.001] |

## By stratum: optimizer vs B2, hours >=95F [95% CI]

| earliest | overall | heat_only | smoke_only | co_occurring | mild |
|---|---|---|---|---|---|
| 04:00 | -0.377 [-0.427, -0.328] (n=1296) | -0.661 [-0.736, -0.589] (n=630) | +0.000 [+0.000, +0.000] (n=38) | -1.014 [-1.157, -0.860] (n=71) | +0.000 [+0.000, +0.000] (n=557) |
| 04:30 | -0.278 [-0.314, -0.242] (n=1296) | -0.489 [-0.542, -0.438] (n=630) | +0.000 [+0.000, +0.000] (n=38) | -0.736 [-0.828, -0.637] (n=71) | +0.000 [+0.000, +0.000] (n=557) |
| 05:00 | -0.150 [-0.169, -0.131] (n=1296) | -0.264 [-0.292, -0.236] (n=630) | +0.000 [+0.000, +0.000] (n=38) | -0.394 [-0.438, -0.347] (n=71) | +0.000 [+0.000, +0.000] (n=557) |
| 05:30 | +0.004 [+0.001, +0.008] (n=1296) | +0.008 [+0.002, +0.015] (n=630) | +0.000 [+0.000, +0.000] (n=38) | +0.000 [+0.000, +0.000] (n=71) | +0.000 [+0.000, +0.000] (n=557) |
| 06:00 | +0.185 [+0.165, +0.205] (n=1296) | +0.330 [+0.304, +0.355] (n=630) | +0.000 [+0.000, +0.000] (n=38) | +0.458 [+0.423, +0.486] (n=71) | +0.000 [+0.000, +0.000] (n=557) |
| sunrise | +0.027 [+0.012, +0.042] (n=1296) | +0.046 [+0.019, +0.073] (n=630) | +0.000 [+0.000, +0.000] (n=38) | +0.085 [+0.000, +0.170] (n=71) | +0.000 [+0.000, +0.000] (n=557) |

## Chosen start times (optimizer, first block)

- 04:00: {'04:00': 1296}
- 04:30: {'04:30': 1296}
- 05:00: {'05:00': 1296}
- 05:30: {'05:30': 1296}
- 06:00: {'06:00': 1296}
- sunrise: {'05:15': 563, '05:30': 186, '05:45': 180, '06:00': 193, '06:15': 173, '06:30': 1} (sunrise-rule earliest starts: {'05:15': 563, '05:30': 186, '05:45': 180, '06:00': 193, '06:15': 173, '06:30': 1})
