SYNTHETIC DAYS INCLUDED: NOT EVIDENCE FOR THE DUAL-HAZARD CLAIM | insufficient real days (0 real_cached, 20 required)

# Madrugada backtest

Days evaluated: 13 synthetic, 0 real_cached (all days with enough history for the proxy forecast; none hand-picked). Runtime 1.44 s.

Metrics are modeled exposure-hours scored on observed values; they are not health outcomes.

Definitions:
- difference: challenger minus baseline; negative = fewer modeled exposure-hours or lower cost
- tie: every physical metric within 0.125 h and observed cost within 1e-06
- win_loss: by observed weighted cost; 'mixed' = equal cost but different physical metrics
- strata: {'heat_temp_f': 95, 'smoke_aqi': 101}
- weight_sensitivity: stratum totals of (optimizer - B2) hours >=95F and AQI>=101 hours per setting

## synthetic: SYNTHETIC, NOT EVIDENCE

### overall (n=13)

| comparison | W/T/L/mixed | mean diff h>=95F | mean diff h AQI>=101 | mean diff cost |
|---|---|---|---|---|
| optimizer_vs_B1 | 10/1/2/0 | -0.8654 [-1.4808, -0.3077] | -0.2308 [-1.1154, +0.75] | -23.8462 [-38.0019, -10.0769] |
| optimizer_vs_B2 | 9/1/2/1 | -0.1731 [-0.5, +0.1154] | -0.1538 [-0.6154, +0.3462] | -9.3846 [-16.3077, -2.3077] |
| optimizer_vs_b3_early | 0/11/2/0 | +0.3077 [+0, +0.75] | +0 [+0, +0] | +2.4615 [+0, +6] |
| optimizer_vs_b3_late | 0/11/2/0 | +0.3077 [+0, +0.75] | +0 [+0, +0] | +2.4615 [+0, +6] |
| robust_vs_B1 | 10/1/2/0 | -0.9808 [-1.6154, -0.3846] | -0.2308 [-1.1154, +0.75] | -24.7692 [-38.9231, -10.7692] |
| robust_vs_B2 | 10/1/2/0 | -0.2885 [-0.5962, -0.0385] | -0.1538 [-0.6154, +0.3462] | -10.3077 [-17.0769, -3.2308] |
| robust_vs_b3_early | 0/11/2/0 | +0.1923 [+0, +0.5] | +0 [+0, +0] | +1.5385 [+0, +4] |
| robust_vs_b3_late | 0/11/2/0 | +0.1923 [+0, +0.5] | +0 [+0, +0] | +1.5385 [+0, +4] |
| oracle_vs_B1 | 10/1/0/2 | -1.1731 [-1.9231, -0.4615] | -0.75 [-1.8269, +0.1154] | -30.9231 [-46.7692, -16.3077] |
| oracle_vs_B2 | 11/2/0/0 | -0.4808 [-0.8462, -0.1731] | -0.6731 [-1.4231, -0.1154] | -16.4615 [-25.5385, -8.6135] |
| oracle_vs_b3_early | 4/9/0/0 | +0 [+0, +0] | -0.5192 [-1.0962, +0] | -4.6154 [-9.8462, -0.1538] |
| oracle_vs_b3_late | 4/9/0/0 | +0 [+0, +0] | -0.5192 [-1.0962, +0] | -4.6154 [-9.8462, -0.1538] |


### heat_only (n=4)

| comparison | W/T/L/mixed | mean diff h>=95F | mean diff h AQI>=101 | mean diff cost |
|---|---|---|---|---|
| optimizer_vs_B1 | 4/0/0/0 | -1.5625 | +0 | -24.5 |
| optimizer_vs_B2 | 3/0/0/1 | -0.4375 | +0 | -9.5 |
| optimizer_vs_b3_early | 0/3/1/0 | +0.5625 | +0 | +4.5 |
| optimizer_vs_b3_late | 0/3/1/0 | +0.5625 | +0 | +4.5 |
| robust_vs_B1 | 4/0/0/0 | -1.9375 | +0 | -27.5 |
| robust_vs_B2 | 4/0/0/0 | -0.8125 | +0 | -12.5 |
| robust_vs_b3_early | 0/3/1/0 | +0.1875 | +0 | +1.5 |
| robust_vs_b3_late | 0/3/1/0 | +0.1875 | +0 | +1.5 |
| oracle_vs_B1 | 4/0/0/0 | -2.125 | +0 | -29 |
| oracle_vs_B2 | 4/0/0/0 | -1 | +0 | -14 |
| oracle_vs_b3_early | 0/4/0/0 | +0 | +0 | +0 |
| oracle_vs_b3_late | 0/4/0/0 | +0 | +0 | +0 |

_n too small for CIs_

### smoke_only (n=3)

| comparison | W/T/L/mixed | mean diff h>=95F | mean diff h AQI>=101 | mean diff cost |
|---|---|---|---|---|
| optimizer_vs_B1 | 2/0/1/0 | +0 | -0.5833 | -22.3333 |
| optimizer_vs_B2 | 2/0/1/0 | +0 | -0.5 | -10.6667 |
| optimizer_vs_b3_early | 0/3/0/0 | +0 | +0 | +0 |
| optimizer_vs_b3_late | 0/3/0/0 | +0 | +0 | +0 |
| robust_vs_B1 | 2/0/1/0 | +0 | -0.5833 | -22.3333 |
| robust_vs_B2 | 2/0/1/0 | +0 | -0.5 | -10.6667 |
| robust_vs_b3_early | 0/3/0/0 | +0 | +0 | +0 |
| robust_vs_b3_late | 0/3/0/0 | +0 | +0 | +0 |
| oracle_vs_B1 | 2/0/0/1 | +0 | -2.3333 | -38.3333 |
| oracle_vs_B2 | 3/0/0/0 | +0 | -2.25 | -26.6667 |
| oracle_vs_b3_early | 3/0/0/0 | +0 | -1.75 | -16 |
| oracle_vs_b3_late | 3/0/0/0 | +0 | -1.75 | -16 |

_n too small for CIs_

### co_occurring (n=3)

| comparison | W/T/L/mixed | mean diff h>=95F | mean diff h AQI>=101 | mean diff cost |
|---|---|---|---|---|
| optimizer_vs_B1 | 2/0/1/0 | -1.6667 | -0.4167 | -40.3333 |
| optimizer_vs_B2 | 2/0/1/0 | -0.1667 | -0.1667 | -13.3333 |
| optimizer_vs_b3_early | 0/2/1/0 | +0.5833 | +0 | +4.6667 |
| optimizer_vs_b3_late | 0/2/1/0 | +0.5833 | +0 | +4.6667 |
| robust_vs_B1 | 2/0/1/0 | -1.6667 | -0.4167 | -40.3333 |
| robust_vs_B2 | 2/0/1/0 | -0.1667 | -0.1667 | -13.3333 |
| robust_vs_b3_early | 0/2/1/0 | +0.5833 | +0 | +4.6667 |
| robust_vs_b3_late | 0/2/1/0 | +0.5833 | +0 | +4.6667 |
| oracle_vs_B1 | 2/0/0/1 | -2.25 | -0.9167 | -49 |
| oracle_vs_B2 | 2/1/0/0 | -0.75 | -0.6667 | -22 |
| oracle_vs_b3_early | 1/2/0/0 | +0 | -0.5 | -4 |
| oracle_vs_b3_late | 1/2/0/0 | +0 | -0.5 | -4 |

_n too small for CIs_

### mild (n=3)

| comparison | W/T/L/mixed | mean diff h>=95F | mean diff h AQI>=101 | mean diff cost |
|---|---|---|---|---|
| optimizer_vs_B1 | 2/1/0/0 | +0 | +0 | -8 |
| optimizer_vs_B2 | 2/1/0/0 | +0 | +0 | -4 |
| optimizer_vs_b3_early | 0/3/0/0 | +0 | +0 | +0 |
| optimizer_vs_b3_late | 0/3/0/0 | +0 | +0 | +0 |
| robust_vs_B1 | 2/1/0/0 | +0 | +0 | -8 |
| robust_vs_B2 | 2/1/0/0 | +0 | +0 | -4 |
| robust_vs_b3_early | 0/3/0/0 | +0 | +0 | +0 |
| robust_vs_b3_late | 0/3/0/0 | +0 | +0 | +0 |
| oracle_vs_B1 | 2/1/0/0 | +0 | +0 | -8 |
| oracle_vs_B2 | 2/1/0/0 | +0 | +0 | -4 |
| oracle_vs_b3_early | 0/3/0/0 | +0 | +0 | +0 |
| oracle_vs_b3_late | 0/3/0/0 | +0 | +0 | +0 |

_n too small for CIs_

### Oracle diagnosis (synthetic)

2 of 2 losses disappear under the oracle.

- syn-2025-08-04-early_pm25_peak: optimizer 39, B2 27, oracle 21 (oracle vs B2: win)
- syn-2025-08-06-co_occurring_offset: optimizer 64, B2 52, oracle 52 (oracle vs B2: tie)

### Weight sensitivity (synthetic): optimizer vs B2

| stratum | days | settings | weakly dominates (totals) | strictly improves (totals) | weakly dominates (per day) | range total diff h>=95F | range total diff h AQI>=101 |
|---|---|---|---|---|---|---|---|
| overall | 13 | 81 | 1.00 | 1.00 | 0.72 | [-5.5, -2.25] | [-2.0, -2.0] |
| heat_only | 4 | 81 | 1.00 | 1.00 | 0.83 | [-3.25, -1.75] | [0.0, 0.0] |
| smoke_only | 3 | 81 | 1.00 | 1.00 | 0.67 | [0.0, 0.0] | [-1.5, -1.5] |
| co_occurring | 3 | 81 | 1.00 | 1.00 | 0.35 | [-2.25, -0.5] | [-0.5, -0.5] |
| mild | 3 | 81 | 1.00 | 0.00 | 1.00 | [0.0, 0.0] | [0.0, 0.0] |

### Forecast-proxy sensitivity (synthetic): optimizer vs B2 (W/T/L/mixed)

| proxy | overall | heat_only | smoke_only | co_occurring | mild |
|---|---|---|---|---|---|
| prev_day_only | 10/1/2/0 (n=13) | 4/0/0/0 (n=4) | 2/0/1/0 (n=3) | 2/0/1/0 (n=3) | 2/1/0/0 (n=3) |
| mean_7day_only | 10/1/2/0 (n=13) | 4/0/0/0 (n=4) | 2/0/1/0 (n=3) | 2/0/1/0 (n=3) | 2/1/0/0 (n=3) |
| default_blend | 9/1/2/1 (n=13) | 3/0/0/1 (n=4) | 2/0/1/0 (n=3) | 2/0/1/0 (n=3) | 2/1/0/0 (n=3) |

## real_cached: insufficient real days

### overall (n=0)

No days.

### heat_only (n=0)

No days.

### smoke_only (n=0)

No days.

### co_occurring (n=0)

No days.

### mild (n=0)

No days.

### Oracle diagnosis (real_cached)

0 of 0 losses disappear under the oracle.


### Weight sensitivity (real_cached): optimizer vs B2

| stratum | days | settings | weakly dominates (totals) | strictly improves (totals) | weakly dominates (per day) | range total diff h>=95F | range total diff h AQI>=101 |
|---|---|---|---|---|---|---|---|
| overall | 0 | - | - | - | - | - | - |
| heat_only | 0 | - | - | - | - | - | - |
| smoke_only | 0 | - | - | - | - | - | - |
| co_occurring | 0 | - | - | - | - | - | - |
| mild | 0 | - | - | - | - | - | - |

### Forecast-proxy sensitivity (real_cached): optimizer vs B2 (W/T/L/mixed)

| proxy | overall | heat_only | smoke_only | co_occurring | mild |
|---|---|---|---|---|---|
| prev_day_only | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) |
| mean_7day_only | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) |
| default_blend | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) | 0/0/0/0 (n=0) |

## Appendix: every day

| day | provenance | stratum | plan | hours_ge_80f | hours_ge_95f | hours_aqi_ge_101 | hours_aqi_ge_151 | dual_hazard_hours | paid_hours | cost | blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| syn-2025-07-25-history | synthetic | mild | optimizer | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | robust | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | oracle | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | B1 | 6 | 0 | 0 | 0 | 0 | 8.5 | 24 | 07:00-15:30 |
| syn-2025-07-25-history | synthetic | mild | B2 | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 05:30-14:00 |
| syn-2025-07-25-history | synthetic | mild | b3_early | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | b3_late | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | | | robust flags: robust_fallback_insufficient_history | | | | | | | | |
| syn-2025-07-26-history | synthetic | mild | optimizer | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | robust | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | oracle | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | B1 | 5 | 0 | 0 | 0 | 0 | 8.5 | 20 | 07:00-15:30 |
| syn-2025-07-26-history | synthetic | mild | B2 | 3.5 | 0 | 0 | 0 | 0 | 8.5 | 14 | 05:30-14:00 |
| syn-2025-07-26-history | synthetic | mild | b3_early | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | b3_late | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | | | robust flags: robust_fallback_insufficient_history | | | | | | | | |
| syn-2025-07-27-history | synthetic | heat_only | optimizer | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | robust | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | oracle | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | B1 | 6.25 | 2.5 | 0 | 0 | 0 | 8.5 | 45 | 07:00-15:30 |
| syn-2025-07-27-history | synthetic | heat_only | B2 | 4.75 | 1 | 0 | 0 | 0 | 8.5 | 27 | 05:30-14:00 |
| syn-2025-07-27-history | synthetic | heat_only | b3_early | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | b3_late | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | | | robust flags: robust_fallback_insufficient_history | | | | | | | | |
| syn-2025-07-28-history | synthetic | heat_only | optimizer | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | robust | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | oracle | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | B1 | 5.5 | 0 | 0 | 0 | 0 | 8.5 | 22 | 07:00-15:30 |
| syn-2025-07-28-history | synthetic | heat_only | B2 | 4 | 0 | 0 | 0 | 0 | 8.5 | 16 | 05:30-14:00 |
| syn-2025-07-28-history | synthetic | heat_only | b3_early | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | b3_late | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | | | robust flags: robust_fallback_insufficient_history | | | | | | | | |
| syn-2025-07-29-history | synthetic | heat_only | optimizer | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | robust | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | oracle | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | B1 | 7.5 | 3 | 0 | 0 | 0 | 8.5 | 54 | 07:00-15:30 |
| syn-2025-07-29-history | synthetic | heat_only | B2 | 6 | 1.5 | 0 | 0 | 0 | 8.5 | 36 | 05:30-14:00 |
| syn-2025-07-29-history | synthetic | heat_only | b3_early | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | b3_late | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | | | robust flags: robust_fallback_insufficient_history | | | | | | | | |
| syn-2025-07-30-history | synthetic | co_occurring | optimizer | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | robust | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | oracle | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | B1 | 6 | 2.25 | 2 | 0 | 2 | 8.5 | 66 | 07:00-15:30 |
| syn-2025-07-30-history | synthetic | co_occurring | B2 | 4.5 | 0.75 | 0.5 | 0 | 0.5 | 8.5 | 30 | 05:30-14:00 |
| syn-2025-07-30-history | synthetic | co_occurring | b3_early | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | b3_late | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | | | robust flags: robust_fallback_insufficient_history | | | | | | | | |
| syn-2025-07-31-history | synthetic | smoke_only | optimizer | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-07-31-history | synthetic | smoke_only | robust | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-07-31-history | synthetic | smoke_only | oracle | 3 | 0 | 1.75 | 0 | 0 | 8.5 | 19 | 04:00-09:30, 16:00-19:00 |
| syn-2025-07-31-history | synthetic | smoke_only | B1 | 4.25 | 0 | 7.75 | 4.5 | 1.25 | 8.5 | 94 | 07:00-15:30 |
| syn-2025-07-31-history | synthetic | smoke_only | B2 | 2.75 | 0 | 6.25 | 4.5 | 0 | 8.5 | 72 | 05:30-14:00 |
| syn-2025-07-31-history | synthetic | smoke_only | b3_early | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-07-31-history | synthetic | smoke_only | b3_late | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-07-31-history | | | robust flags: robust_fallback_insufficient_history | | | | | | | | |
| syn-2025-08-01-heat_only | synthetic | heat_only | optimizer | 5.25 | 3.5 | 0 | 0 | 0 | 8.5 | 49 | 04:00-09:00, 14:45-18:15 |
| syn-2025-08-01-heat_only | synthetic | heat_only | robust | 5.25 | 2 | 0 | 0 | 0 | 8.5 | 37 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-01-heat_only | synthetic | heat_only | oracle | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |
| syn-2025-08-01-heat_only | synthetic | heat_only | B1 | 8.25 | 4.25 | 0 | 0 | 0 | 8.5 | 67 | 07:00-15:30 |
| syn-2025-08-01-heat_only | synthetic | heat_only | B2 | 6.75 | 2.75 | 0 | 0 | 0 | 8.5 | 49 | 05:30-14:00 |
| syn-2025-08-01-heat_only | synthetic | heat_only | b3_early | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |
| syn-2025-08-01-heat_only | synthetic | heat_only | b3_late | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | optimizer | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | robust | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | oracle | 0.25 | 0 | 6.75 | 4.75 | 0 | 8.5 | 66 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | B1 | 2 | 0 | 8.5 | 8 | 0 | 8.5 | 106 | 07:00-15:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | B2 | 0.5 | 0 | 8.25 | 6.5 | 0 | 8.5 | 87 | 05:30-14:00 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | b3_early | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | b3_late | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | optimizer | 4.5 | 2 | 6.25 | 3.5 | 2 | 8.5 | 103 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | robust | 4.5 | 2 | 6.25 | 3.5 | 2 | 8.5 | 103 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | oracle | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | B1 | 7.5 | 3.25 | 8.5 | 6.5 | 5 | 8.5 | 182 | 07:00-15:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | B2 | 6 | 1.75 | 7.75 | 5 | 3.5 | 8.5 | 137 | 05:30-14:00 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | b3_early | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | b3_late | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | optimizer | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | robust | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | oracle | 4.25 | 0 | 1 | 0 | 0 | 8.5 | 21 | 06:15-14:45 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | B1 | 5 | 0 | 0.25 | 0 | 0 | 8.5 | 21 | 07:00-15:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | B2 | 3.5 | 0 | 1.75 | 0.75 | 0 | 8.5 | 27 | 05:30-14:00 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | b3_early | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | b3_late | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-05-mild | synthetic | mild | optimizer | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 05:15-13:45 |
| syn-2025-08-05-mild | synthetic | mild | robust | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:45-13:15 |
| syn-2025-08-05-mild | synthetic | mild | oracle | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |
| syn-2025-08-05-mild | synthetic | mild | B1 | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 07:00-15:30 |
| syn-2025-08-05-mild | synthetic | mild | B2 | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 05:30-14:00 |
| syn-2025-08-05-mild | synthetic | mild | b3_early | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |
| syn-2025-08-05-mild | synthetic | mild | b3_late | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | optimizer | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | robust | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | oracle | 4 | 0 | 3.5 | 2.75 | 0 | 8.5 | 52 | 05:30-14:00 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | B1 | 5.5 | 1.5 | 2 | 1.25 | 0 | 8.5 | 52 | 07:00-15:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | B2 | 4 | 0 | 3.5 | 2.75 | 0 | 8.5 | 52 | 05:30-14:00 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | b3_early | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | b3_late | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |

Challengers: optimizer, robust, oracle. Baselines: B1, B2, b3_early, b3_late. 'oracle' plans on the day's own observed data: an upper bound, not a forecast.
