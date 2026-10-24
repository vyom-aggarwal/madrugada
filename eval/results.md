SYNTHETIC DAYS INCLUDED: NOT EVIDENCE FOR THE DUAL-HAZARD CLAIM | insufficient real days (0 real_cached, 20 required)

# Madrugada backtest

## What this does and does not show

- Days evaluated: 13 (13 synthetic, 0 real_cached); every day with enough history for the forecast proxy, none hand-picked.
- The 13 synthetic days (7 of them generated history days) are illustrations: they show how the planner behaves, not that it reduces exposure in the field.
- insufficient real days: 0 real_cached, 20 required for any real-data conclusion. This page shows no real-data result.
- Heat-only planning is the closest baseline; see the B3 rows.
- In the current synthetic data the optimizer never has fewer AQI>=101 hours than either B3 variant (0 of 13 days).
- Numbers are modeled exposure-hours from station-level data. They are not health outcomes, not field microclimate, and not a compliance assessment.

Runtime 3.74 s.

Definitions:
- primary_outcome: physical dominance: win = no more hours >=95F and no more AQI>=101 hours and strictly less on at least one; loss = the reverse; tie = all physical metrics within 0.125 h; otherwise mixed
- secondary_outcome: uses the optimizer's own cost: win/loss by observed weighted cost; tie also needs cost within 1e-06; mixed = equal cost, different physical metrics
- difference: challenger minus baseline; negative = fewer modeled exposure-hours or lower cost
- robust: compared only on days where it did not fall back, and with the optimizer on those same days
- ci: synthetic: paired bootstrap over days; real: cluster bootstrap over calendar dates
- nowcast: SECONDARY, observed only: hours at NowCast AQI >= 101 / 151 (unverified NowCast); planning uses hourly values
- strata: {'heat_temp_f': 95, 'smoke_aqi': 101}
- weight_sensitivity: headline = day-level fraction of (setting, day) pairs; stratum totals secondary

## synthetic: SYNTHETIC, NOT EVIDENCE (n=13)

### PRIMARY: physical dominance (W/T/L/mixed)

| comparison | overall (n=13) | heat_only (n=4) | smoke_only (n=3) | co_occurring (n=3) | mild (n=3) |
|---|---|---|---|---|---|
| optimizer vs B1 | 7/1/1/4 (n=13) | 3/0/0/1 (n=4) | 2/0/1/0 (n=3) | 2/0/0/1 (n=3) | 0/1/0/2 (n=3) |
| optimizer vs B2 | 5/1/3/4 (n=13) | 2/0/1/1 (n=4) | 2/0/1/0 (n=3) | 1/0/1/1 (n=3) | 0/1/0/2 (n=3) |
| optimizer vs b3_early | 0/11/2/0 (n=13) | 0/3/1/0 (n=4) | 0/3/0/0 (n=3) | 0/2/1/0 (n=3) | 0/3/0/0 (n=3) |
| optimizer vs b3_late | 0/11/2/0 (n=13) | 0/3/1/0 (n=4) | 0/3/0/0 (n=3) | 0/2/1/0 (n=3) | 0/3/0/0 (n=3) |
| robust vs B1 | 3/1/1/1 (n=6) | 1/0/0/0 (n=1) | 1/0/1/0 (n=2) | 1/0/0/1 (n=2) | 0/1/0/0 (n=1) |
| robust vs B2 | 2/1/2/1 (n=6) | 1/0/0/0 (n=1) | 1/0/1/0 (n=2) | 0/0/1/1 (n=2) | 0/1/0/0 (n=1) |
| robust vs b3_early | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |
| robust vs b3_late | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |
| oracle vs B1 | 7/1/1/4 (n=13) | 3/0/0/1 (n=4) | 2/0/1/0 (n=3) | 2/0/0/1 (n=3) | 0/1/0/2 (n=3) |
| oracle vs B2 | 8/2/0/3 (n=13) | 3/0/0/1 (n=4) | 3/0/0/0 (n=3) | 2/1/0/0 (n=3) | 0/1/0/2 (n=3) |
| oracle vs b3_early | 3/9/0/1 (n=13) | 0/4/0/0 (n=4) | 2/0/0/1 (n=3) | 1/2/0/0 (n=3) | 0/3/0/0 (n=3) |
| oracle vs b3_late | 3/9/0/1 (n=13) | 0/4/0/0 (n=4) | 2/0/0/1 (n=3) | 1/2/0/0 (n=3) | 0/3/0/0 (n=3) |

Robust rows use only days without fallback (7 fallback days: syn-2025-07-25-history, syn-2025-07-26-history, syn-2025-07-27-history, syn-2025-07-28-history, syn-2025-07-29-history, syn-2025-07-30-history, syn-2025-07-31-history). Same-day comparison with the optimizer:

| comparison | overall (n=13) | heat_only (n=4) | smoke_only (n=3) | co_occurring (n=3) | mild (n=3) |
|---|---|---|---|---|---|
| robust vs optimizer | 1/5/0/0 (n=6) | 1/0/0/0 (n=1) | 0/2/0/0 (n=2) | 0/2/0/0 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs B1 | 3/1/1/1 (n=6) | 1/0/0/0 (n=1) | 1/0/1/0 (n=2) | 1/0/0/1 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs B2 | 1/1/3/1 (n=6) | 0/0/1/0 (n=1) | 1/0/1/0 (n=2) | 0/0/1/1 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs b3_early | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs b3_late | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |

### Secondary: cost-based outcomes (uses the optimizer's own cost)

| comparison | overall (n=13) | heat_only (n=4) | smoke_only (n=3) | co_occurring (n=3) | mild (n=3) |
|---|---|---|---|---|---|
| optimizer vs B1 | 10/1/2/0 (n=13) | 4/0/0/0 (n=4) | 2/0/1/0 (n=3) | 2/0/1/0 (n=3) | 2/1/0/0 (n=3) |
| optimizer vs B2 | 9/1/2/1 (n=13) | 3/0/0/1 (n=4) | 2/0/1/0 (n=3) | 2/0/1/0 (n=3) | 2/1/0/0 (n=3) |
| optimizer vs b3_early | 0/11/2/0 (n=13) | 0/3/1/0 (n=4) | 0/3/0/0 (n=3) | 0/2/1/0 (n=3) | 0/3/0/0 (n=3) |
| optimizer vs b3_late | 0/11/2/0 (n=13) | 0/3/1/0 (n=4) | 0/3/0/0 (n=3) | 0/2/1/0 (n=3) | 0/3/0/0 (n=3) |
| robust vs B1 | 3/1/2/0 (n=6) | 1/0/0/0 (n=1) | 1/0/1/0 (n=2) | 1/0/1/0 (n=2) | 0/1/0/0 (n=1) |
| robust vs B2 | 3/1/2/0 (n=6) | 1/0/0/0 (n=1) | 1/0/1/0 (n=2) | 1/0/1/0 (n=2) | 0/1/0/0 (n=1) |
| robust vs b3_early | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |
| robust vs b3_late | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |
| oracle vs B1 | 10/1/0/2 (n=13) | 4/0/0/0 (n=4) | 2/0/0/1 (n=3) | 2/0/0/1 (n=3) | 2/1/0/0 (n=3) |
| oracle vs B2 | 11/2/0/0 (n=13) | 4/0/0/0 (n=4) | 3/0/0/0 (n=3) | 2/1/0/0 (n=3) | 2/1/0/0 (n=3) |
| oracle vs b3_early | 4/9/0/0 (n=13) | 0/4/0/0 (n=4) | 3/0/0/0 (n=3) | 1/2/0/0 (n=3) | 0/3/0/0 (n=3) |
| oracle vs b3_late | 4/9/0/0 (n=13) | 0/4/0/0 (n=4) | 3/0/0/0 (n=3) | 1/2/0/0 (n=3) | 0/3/0/0 (n=3) |
| robust vs optimizer | 1/5/0/0 (n=6) | 1/0/0/0 (n=1) | 0/2/0/0 (n=2) | 0/2/0/0 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs B1 | 3/1/2/0 (n=6) | 1/0/0/0 (n=1) | 1/0/1/0 (n=2) | 1/0/1/0 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs B2 | 2/1/2/1 (n=6) | 0/0/0/1 (n=1) | 1/0/1/0 (n=2) | 1/0/1/0 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs b3_early | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |
| optimizer_on_robust_days vs b3_late | 0/4/2/0 (n=6) | 0/0/1/0 (n=1) | 0/2/0/0 (n=2) | 0/1/1/0 (n=2) | 0/1/0/0 (n=1) |

### Mean paired differences, overall (challenger - baseline; 95% CI by paired bootstrap where enough)

| comparison | n | dates | h>=95F | h AQI>=101 | cost |
|---|---|---|---|---|---|
| optimizer_vs_B1 | 13 | 13 | -0.8654 [-1.4808, -0.3077] | -0.2308 [-1.1154, +0.75] | -23.8462 [-38.0019, -10.0769] |
| optimizer_vs_B2 | 13 | 13 | -0.1731 [-0.5, +0.1154] | -0.1538 [-0.6154, +0.3462] | -9.3846 [-16.3077, -2.3077] |
| optimizer_vs_b3_early | 13 | 13 | +0.3077 [+0, +0.75] | +0 [+0, +0] | +2.4615 [+0, +6] |
| optimizer_vs_b3_late | 13 | 13 | +0.3077 [+0, +0.75] | +0 [+0, +0] | +2.4615 [+0, +6] |
| robust_vs_B1 | 6 | 6 | -0.8333 | +0.3333 | -19.6667 | n too small for CIs
| robust_vs_B2 | 6 | 6 | -0.0833 | +0 | -7 | n too small for CIs
| robust_vs_b3_early | 6 | 6 | +0.4167 | +0 | +3.3333 | n too small for CIs
| robust_vs_b3_late | 6 | 6 | +0.4167 | +0 | +3.3333 | n too small for CIs
| oracle_vs_B1 | 13 | 13 | -1.1731 [-1.9231, -0.4615] | -0.75 [-1.8269, +0.1154] | -30.9231 [-46.7692, -16.3077] |
| oracle_vs_B2 | 13 | 13 | -0.4808 [-0.8462, -0.1731] | -0.6731 [-1.4231, -0.1154] | -16.4615 [-25.5385, -8.6135] |
| oracle_vs_b3_early | 13 | 13 | +0 [+0, +0] | -0.5192 [-1.0962, +0] | -4.6154 [-9.8462, -0.1538] |
| oracle_vs_b3_late | 13 | 13 | +0 [+0, +0] | -0.5192 [-1.0962, +0] | -4.6154 [-9.8462, -0.1538] |
| robust_vs_optimizer | 6 | 6 | -0.25 | +0 | -2 | n too small for CIs
| optimizer_on_robust_days_vs_B1 | 6 | 6 | -0.5833 | +0.3333 | -17.6667 | n too small for CIs
| optimizer_on_robust_days_vs_B2 | 6 | 6 | +0.1667 | +0 | -5 | n too small for CIs
| optimizer_on_robust_days_vs_b3_early | 6 | 6 | +0.6667 | +0 | +5.3333 | n too small for CIs
| optimizer_on_robust_days_vs_b3_late | 6 | 6 | +0.6667 | +0 | +5.3333 | n too small for CIs

### Oracle diagnosis (optimizer losses to B2)

- Physical (primary): 2 of 3 losses become oracle wins, 1 become ties.
- Cost (uses the optimizer's own cost): 1 of 2 losses become oracle wins, 1 become ties.

### Days where the optimizer loses physically to B2 (3; observed numbers)

- syn-2025-08-01-heat_only (heat_only): optimizer h>=95F 3.5, AQI>=101 0; B2 h>=95F 2.75, AQI>=101 0
- syn-2025-08-04-early_pm25_peak (smoke_only): optimizer h>=95F 0, AQI>=101 3.25; B2 h>=95F 0, AQI>=101 1.75
- syn-2025-08-06-co_occurring_offset (co_occurring): optimizer h>=95F 0, AQI>=101 5; B2 h>=95F 0, AQI>=101 3.5

### Weight sensitivity: optimizer vs B2 (81 settings)

| stratum | days | HEADLINE day-level weakly dominates | day-level strictly improves | totals weakly dominates | totals strictly improves | range total diff h>=95F | range total diff h AQI>=101 |
|---|---|---|---|---|---|---|---|
| overall | 13 | 0.72 | 0.41 | 1.00 | 1.00 | [-5.5, -2.25] | [-2.0, -2.0] |
| heat_only | 4 | 0.83 | 0.58 | 1.00 | 1.00 | [-3.25, -1.75] | [0.0, 0.0] |
| smoke_only | 3 | 0.67 | 0.67 | 1.00 | 1.00 | [0.0, 0.0] | [-1.5, -1.5] |
| co_occurring | 3 | 0.35 | 0.35 | 1.00 | 1.00 | [-2.25, -0.5] | [-0.5, -0.5] |
| mild | 3 | 1.00 | 0.00 | 1.00 | 0.00 | [0.0, 0.0] | [0.0, 0.0] |

### Forecast-proxy sensitivity: optimizer vs B2, overall (physical W/T/L/M | cost W/T/L/M)

- prev_day_only (n=13): physical 5/1/3/4 | cost 10/1/2/0
- mean_7day_only (n=13): physical 6/1/2/4 | cost 10/1/2/0
- default_blend (n=13): physical 5/1/3/4 | cost 9/1/2/1

### SECONDARY: NowCast-based smoke hours (observed only; mean hours per day, overall)

| plan | h AQI>=101 (hourly) | h AQI>=101 (NowCast) | h AQI>=151 (hourly) | h AQI>=151 (NowCast) |
|---|---|---|---|---|
| optimizer | 2 | 2.0385 | 1.3846 | 1.2692 |
| robust | 2 | 2.0385 | 1.3846 | 1.2692 |
| oracle | 1.4808 | 1.5962 | 0.8462 | 0.8654 |
| B1 | 2.2308 | 2.3077 | 1.5577 | 1.4615 |
| B2 | 2.1538 | 2.1538 | 1.5 | 1.3846 |
| b3_early | 2 | 2.0385 | 1.3846 | 1.2692 |
| b3_late | 2 | 2.0385 | 1.3846 | 1.2692 |

## real_cached: insufficient real days (n=0)

Status: insufficient real days (0 < 20); not evaluated

No days evaluated.

## Appendix: every day

| day | provenance | stratum | sources | plan | hours_ge_80f | hours_ge_95f | hours_aqi_ge_101 | hours_aqi_ge_151 | dual_hazard_hours | paid_hours | cost | blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| syn-2025-07-25-history | synthetic | mild | synthetic | optimizer | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | synthetic | robust (robust fell back) | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | synthetic | oracle | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | synthetic | B1 | 6 | 0 | 0 | 0 | 0 | 8.5 | 24 | 07:00-15:30 |
| syn-2025-07-25-history | synthetic | mild | synthetic | B2 | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 05:30-14:00 |
| syn-2025-07-25-history | synthetic | mild | synthetic | b3_early | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-25-history | synthetic | mild | synthetic | b3_late | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | synthetic | optimizer | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | synthetic | robust (robust fell back) | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | synthetic | oracle | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | synthetic | B1 | 5 | 0 | 0 | 0 | 0 | 8.5 | 20 | 07:00-15:30 |
| syn-2025-07-26-history | synthetic | mild | synthetic | B2 | 3.5 | 0 | 0 | 0 | 0 | 8.5 | 14 | 05:30-14:00 |
| syn-2025-07-26-history | synthetic | mild | synthetic | b3_early | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-26-history | synthetic | mild | synthetic | b3_late | 2 | 0 | 0 | 0 | 0 | 8.5 | 8 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | synthetic | optimizer | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | synthetic | robust (robust fell back) | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | synthetic | oracle | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | synthetic | B1 | 6.25 | 2.5 | 0 | 0 | 0 | 8.5 | 45 | 07:00-15:30 |
| syn-2025-07-27-history | synthetic | heat_only | synthetic | B2 | 4.75 | 1 | 0 | 0 | 0 | 8.5 | 27 | 05:30-14:00 |
| syn-2025-07-27-history | synthetic | heat_only | synthetic | b3_early | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-27-history | synthetic | heat_only | synthetic | b3_late | 3.25 | 0 | 0 | 0 | 0 | 8.5 | 13 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | synthetic | optimizer | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | synthetic | robust (robust fell back) | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | synthetic | oracle | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | synthetic | B1 | 5.5 | 0 | 0 | 0 | 0 | 8.5 | 22 | 07:00-15:30 |
| syn-2025-07-28-history | synthetic | heat_only | synthetic | B2 | 4 | 0 | 0 | 0 | 0 | 8.5 | 16 | 05:30-14:00 |
| syn-2025-07-28-history | synthetic | heat_only | synthetic | b3_early | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-28-history | synthetic | heat_only | synthetic | b3_late | 2.5 | 0 | 0 | 0 | 0 | 8.5 | 10 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | synthetic | optimizer | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | synthetic | robust (robust fell back) | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | synthetic | oracle | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | synthetic | B1 | 7.5 | 3 | 0 | 0 | 0 | 8.5 | 54 | 07:00-15:30 |
| syn-2025-07-29-history | synthetic | heat_only | synthetic | B2 | 6 | 1.5 | 0 | 0 | 0 | 8.5 | 36 | 05:30-14:00 |
| syn-2025-07-29-history | synthetic | heat_only | synthetic | b3_early | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-29-history | synthetic | heat_only | synthetic | b3_late | 4.5 | 0 | 0 | 0 | 0 | 8.5 | 18 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | synthetic | optimizer | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | synthetic | robust (robust fell back) | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | synthetic | oracle | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | synthetic | B1 | 6 | 2.25 | 2 | 0 | 2 | 8.5 | 66 | 07:00-15:30 |
| syn-2025-07-30-history | synthetic | co_occurring | synthetic | B2 | 4.5 | 0.75 | 0.5 | 0 | 0.5 | 8.5 | 30 | 05:30-14:00 |
| syn-2025-07-30-history | synthetic | co_occurring | synthetic | b3_early | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-30-history | synthetic | co_occurring | synthetic | b3_late | 3 | 0 | 0 | 0 | 0 | 8.5 | 12 | 04:00-12:30 |
| syn-2025-07-31-history | synthetic | smoke_only | synthetic | optimizer | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-07-31-history | synthetic | smoke_only | synthetic | robust (robust fell back) | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-07-31-history | synthetic | smoke_only | synthetic | oracle | 3 | 0 | 1.75 | 0 | 0 | 8.5 | 19 | 04:00-09:30, 16:00-19:00 |
| syn-2025-07-31-history | synthetic | smoke_only | synthetic | B1 | 4.25 | 0 | 7.75 | 4.5 | 1.25 | 8.5 | 94 | 07:00-15:30 |
| syn-2025-07-31-history | synthetic | smoke_only | synthetic | B2 | 2.75 | 0 | 6.25 | 4.5 | 0 | 8.5 | 72 | 05:30-14:00 |
| syn-2025-07-31-history | synthetic | smoke_only | synthetic | b3_early | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-07-31-history | synthetic | smoke_only | synthetic | b3_late | 1.25 | 0 | 4.75 | 3 | 0 | 8.5 | 48 | 04:00-12:30 |
| syn-2025-08-01-heat_only | synthetic | heat_only | synthetic | optimizer | 5.25 | 3.5 | 0 | 0 | 0 | 8.5 | 49 | 04:00-09:00, 14:45-18:15 |
| syn-2025-08-01-heat_only | synthetic | heat_only | synthetic | robust | 5.25 | 2 | 0 | 0 | 0 | 8.5 | 37 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-01-heat_only | synthetic | heat_only | synthetic | oracle | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |
| syn-2025-08-01-heat_only | synthetic | heat_only | synthetic | B1 | 8.25 | 4.25 | 0 | 0 | 0 | 8.5 | 67 | 07:00-15:30 |
| syn-2025-08-01-heat_only | synthetic | heat_only | synthetic | B2 | 6.75 | 2.75 | 0 | 0 | 0 | 8.5 | 49 | 05:30-14:00 |
| syn-2025-08-01-heat_only | synthetic | heat_only | synthetic | b3_early | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |
| syn-2025-08-01-heat_only | synthetic | heat_only | synthetic | b3_late | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | synthetic | optimizer | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | synthetic | robust | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | synthetic | oracle | 0.25 | 0 | 6.75 | 4.75 | 0 | 8.5 | 66 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | synthetic | B1 | 2 | 0 | 8.5 | 8 | 0 | 8.5 | 106 | 07:00-15:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | synthetic | B2 | 0.5 | 0 | 8.25 | 6.5 | 0 | 8.5 | 87 | 05:30-14:00 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | synthetic | b3_early | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-02-smoke_only | synthetic | smoke_only | synthetic | b3_late | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | synthetic | optimizer | 4.5 | 2 | 6.25 | 3.5 | 2 | 8.5 | 103 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | synthetic | robust | 4.5 | 2 | 6.25 | 3.5 | 2 | 8.5 | 103 | 04:00-10:30, 17:00-19:00 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | synthetic | oracle | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | synthetic | B1 | 7.5 | 3.25 | 8.5 | 6.5 | 5 | 8.5 | 182 | 07:00-15:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | synthetic | B2 | 6 | 1.75 | 7.75 | 5 | 3.5 | 8.5 | 137 | 05:30-14:00 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | synthetic | b3_early | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |
| syn-2025-08-03-co_occurring | synthetic | co_occurring | synthetic | b3_late | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | synthetic | optimizer | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | synthetic | robust | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | synthetic | oracle | 4.25 | 0 | 1 | 0 | 0 | 8.5 | 21 | 06:15-14:45 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | synthetic | B1 | 5 | 0 | 0.25 | 0 | 0 | 8.5 | 21 | 07:00-15:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | synthetic | B2 | 3.5 | 0 | 1.75 | 0.75 | 0 | 8.5 | 27 | 05:30-14:00 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | synthetic | b3_early | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-04-early_pm25_peak | synthetic | smoke_only | synthetic | b3_late | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| syn-2025-08-05-mild | synthetic | mild | synthetic | optimizer | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 05:15-13:45 |
| syn-2025-08-05-mild | synthetic | mild | synthetic | robust | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:45-13:15 |
| syn-2025-08-05-mild | synthetic | mild | synthetic | oracle | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |
| syn-2025-08-05-mild | synthetic | mild | synthetic | B1 | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 07:00-15:30 |
| syn-2025-08-05-mild | synthetic | mild | synthetic | B2 | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 05:30-14:00 |
| syn-2025-08-05-mild | synthetic | mild | synthetic | b3_early | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |
| syn-2025-08-05-mild | synthetic | mild | synthetic | b3_late | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | synthetic | optimizer | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | synthetic | robust | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | synthetic | oracle | 4 | 0 | 3.5 | 2.75 | 0 | 8.5 | 52 | 05:30-14:00 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | synthetic | B1 | 5.5 | 1.5 | 2 | 1.25 | 0 | 8.5 | 52 | 07:00-15:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | synthetic | B2 | 4 | 0 | 3.5 | 2.75 | 0 | 8.5 | 52 | 05:30-14:00 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | synthetic | b3_early | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| syn-2025-08-06-co_occurring_offset | synthetic | co_occurring | synthetic | b3_late | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |

Challengers: optimizer, robust, oracle. Baselines: B1, B2, b3_early, b3_late. 'oracle' plans on the day's own observed data: an upper bound, not a forecast.
