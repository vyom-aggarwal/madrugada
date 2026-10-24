SYNTHETIC ILLUSTRATIONS, NOT EVIDENCE

# Fixture findings

Plans built on the forecast proxy (no ORACLE), scored on observed values. Paid hours 8.5, window 04:00-19:00. Weighted cost uses config.yaml weights.

## syn-2025-08-01-heat_only (synthetic)

SYNTHETIC: hot afternoon, clean air

| plan | h >=80F | h >=95F | h AQI>=101 | h AQI>=151 | dual h | paid h | cost (observed) | blocks |
|---|---|---|---|---|---|---|---|---|
| optimizer | 5.25 | 3.5 | 0 | 0 | 0 | 8.5 | 49 | 04:00-09:00, 14:45-18:15 |
| B1 | 8.25 | 4.25 | 0 | 0 | 0 | 8.5 | 67 | 07:00-15:30 |
| B2 | 6.75 | 2.75 | 0 | 0 | 0 | 8.5 | 49 | 05:30-14:00 |
| b3_early | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |
| b3_late | 5.25 | 1.25 | 0 | 0 | 0 | 8.5 | 31 | 04:00-12:30 |

## syn-2025-08-02-smoke_only (synthetic)

SYNTHETIC: moderate temps, smoke event

| plan | h >=80F | h >=95F | h AQI>=101 | h AQI>=151 | dual h | paid h | cost (observed) | blocks |
|---|---|---|---|---|---|---|---|---|
| optimizer | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| B1 | 2 | 0 | 8.5 | 8 | 0 | 8.5 | 106 | 07:00-15:30 |
| B2 | 0.5 | 0 | 8.25 | 6.5 | 0 | 8.5 | 87 | 05:30-14:00 |
| b3_early | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |
| b3_late | 0 | 0 | 6.75 | 5 | 0 | 8.5 | 67 | 04:00-12:30 |

## syn-2025-08-03-co_occurring (synthetic)

SYNTHETIC: hot afternoon with smoke

| plan | h >=80F | h >=95F | h AQI>=101 | h AQI>=151 | dual h | paid h | cost (observed) | blocks |
|---|---|---|---|---|---|---|---|---|
| optimizer | 4.5 | 2 | 6.25 | 3.5 | 2 | 8.5 | 103 | 04:00-10:30, 17:00-19:00 |
| B1 | 7.5 | 3.25 | 8.5 | 6.5 | 5 | 8.5 | 182 | 07:00-15:30 |
| B2 | 6 | 1.75 | 7.75 | 5 | 3.5 | 8.5 | 137 | 05:30-14:00 |
| b3_early | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |
| b3_late | 4.5 | 0.25 | 6.25 | 3.5 | 2 | 8.5 | 89 | 04:00-12:30 |

## syn-2025-08-04-early_pm25_peak (synthetic)

SYNTHETIC: pre-dawn PM2.5 peak, clearing by day

| plan | h >=80F | h >=95F | h AQI>=101 | h AQI>=151 | dual h | paid h | cost (observed) | blocks |
|---|---|---|---|---|---|---|---|---|
| optimizer | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| B1 | 5 | 0 | 0.25 | 0 | 0 | 8.5 | 21 | 07:00-15:30 |
| B2 | 3.5 | 0 | 1.75 | 0.75 | 0 | 8.5 | 27 | 05:30-14:00 |
| b3_early | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |
| b3_late | 2 | 0 | 3.25 | 2.25 | 0 | 8.5 | 39 | 04:00-12:30 |

## syn-2025-08-05-mild (synthetic)

SYNTHETIC: mild temps, clean air

| plan | h >=80F | h >=95F | h AQI>=101 | h AQI>=151 | dual h | paid h | cost (observed) | blocks |
|---|---|---|---|---|---|---|---|---|
| optimizer | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 05:15-13:45 |
| B1 | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 07:00-15:30 |
| B2 | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 05:30-14:00 |
| b3_early | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |
| b3_late | 0 | 0 | 0 | 0 | 0 | 8.5 | 0 | 04:00-12:30 |

## syn-2025-08-06-co_occurring_offset (synthetic)

SYNTHETIC: late-afternoon heat, early-morning smoke

| plan | h >=80F | h >=95F | h AQI>=101 | h AQI>=151 | dual h | paid h | cost (observed) | blocks |
|---|---|---|---|---|---|---|---|---|
| optimizer | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| B1 | 5.5 | 1.5 | 2 | 1.25 | 0 | 8.5 | 52 | 07:00-15:30 |
| B2 | 4 | 0 | 3.5 | 2.75 | 0 | 8.5 | 52 | 05:30-14:00 |
| b3_early | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |
| b3_late | 2.5 | 0 | 5 | 4.25 | 0 | 8.5 | 64 | 04:00-12:30 |

## Summary

Days where the optimizer has fewer observed AQI>=101 hours than BOTH B3 variants: none.
