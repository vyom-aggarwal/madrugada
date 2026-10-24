# Verification notes: PM2.5 AQI breakpoints and NowCast

Read-only check. No config or code was changed (the preregistration hashes still match).

- Source: U.S. EPA, *Technical Assistance Document for the Reporting of Daily Air Quality: the Air Quality
  Index (AQI)*, EPA-403/B-26-003, May 2026.
  URL: https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf
- Retrieved: 2026-10-24 (19:54 UTC), by `curl`. The text was extracted from the PDF's content streams. The
  AQI-500 concentration is printed with font glyph codes; it was decoded using the digit glyphs of the PM10
  entry ("604") on the same line.

## PM2.5 breakpoints (config.yaml `aqi_pm25.breakpoints` vs EPA Table 6, PM2.5 24-hour, ug/m3)

| AQI | config.yaml | EPA (May 2026) | result |
|---|---|---|---|
| 0-50 | 0.0-9.0 | 0.0-9.0 | matched |
| 51-100 | 9.1-35.4 | 9.1-35.4 | matched |
| 101-150 | 35.5-55.4 | 35.5-55.4 | matched |
| 151-200 | 55.5-125.4 | 55.5-125.4 | matched |
| 201-300 | 125.5-225.4 | 125.5-225.4 | matched |
| 301-500 | 225.5-325.4 | 225.5+ (301+); AQI 500 = 325.4 ug/m3 (footnote 4) | matched |
| > 500 | same slope as 301-500, flagged as extrapolated | "same linear slope as the AQI values between 301 and 500" | matched |

- Truncation: EPA truncates PM2.5 to 1 decimal place before the lookup; app/aqi.py does the same. Matched.
- Rounding: EPA's worked example rounds the AQI to the nearest integer (125.5 -> 126); app/aqi.py rounds
  half up. Matched.
- **Method note (not a table discrepancy):** EPA's breakpoints are for 24-hour average PM2.5. The planner
  and the preregistered evaluation apply them to hourly concentrations, which is a modeling choice. EPA's
  "current AQI" uses the NowCast, which is why NowCast hours are reported as a secondary metric.

## NowCast (app/aqi.py `nowcast_pm25`) vs EPA "How the NowCast is calculated" (same document)

| step | EPA | app/aqi.py | result |
|---|---|---|---|
| window | past 12 hours | 12 most recent hours | matched |
| weight factor | 1 - (max - min) / max | 1 - (cmax - cmin) / cmax | matched |
| limits | between 0.5 and 1; below 0.5 -> 0.5 | floor 0.5 | matched |
| weights | weight ^ hours ago (current hour ^0) | w ^ k, k = 0 for the current hour | matched |
| NowCast | sum(products) / sum(weights) | same, over valid hours | matched |
| missing data | 2 of the last 3 hours must be valid | requires >= 2 of the 3 most recent valid | matched |
| max = 0 | not specified | weight 1 | assumption (all values are 0, so the result is 0 either way) |
| truncation before AQI | not restated in the NowCast section | truncated to 0.1 by `pm25_to_aqi` (EPA's general PM2.5 rule) | assumption, consistent |

## Effect on headline results

Nothing differed, so nothing was recomputed and no preregistered headline changes. The "unverified" labels
in config.yaml and app/aqi.py are left as they are, because editing those files would change the
preregistration hashes. This note is the record that both items were checked against the May 2026 EPA document.
