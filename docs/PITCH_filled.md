# Madrugada pitch (filled from results; exploratory numbers are labeled EXPLORATORY, POST-HOC: not preregistered)

Numbers in `{{...}}` come from eval/results.json (preregistered) and analysis/exploratory_results.json
(EXPLORATORY, POST-HOC: not preregistered). Run `python -m analysis.fill_pitch` to write docs/PITCH_filled.md.
Do not type numbers into this file.

## (a) 100-second demo script

1. (10 s) "Madrugada is a **heat-first shift planner with smoke exposure shown**. For a Central Valley crew it
   moves the same paid hours into the coolest part of the day and shows the smoke picture next to it."
2. (15 s) Open the page on the default day **real-2024-07-14-bakersfield** (picked by a stated rule: most observed
   dual-hazard hours). Point at the REAL and REPLAY badges and the dashed lines: 80F shade trigger, 95F
   high-heat procedures, AQI 101 and 151.
3. (15 s) Comparison table: the optimizer vs the fixed shifts B1 and B2 and the heat-only planner B3.
   Toggle "observed".
4. (15 s) Backtest headline: "On 1296 real region-days (509 dates, summers 2022 to 2025), the
   plan cut time at or above 95F by **0.38 h/day** vs a fixed 05:30 start (95% CI -0.43 to -0.33)."
5. (15 s) Say the limit out loud: "There was **no measurable smoke benefit** (-0.001 h/day, CI
   -0.007 to +0.005). It ties heat-only planning on 1292 of 1296 days. Even with perfect hindsight the
   oracle changes smoke hours by only -0.026 h/day."
6. (10 s) Why: "Smoke was rare (109 of 1296 days had any AQI>=101 hour), and the cleanest hours
   are late afternoon (16:00-18:00), when it is hottest. The coolest hours (05:00-07:00) are not the cleanest."
7. (10 s) Click "Print crew sheet": a bilingual summary with 12-hour times and the advisory disclaimer.
8. (10 s) Close: "An advisory aid that reduces modeled heat exposure-hours and shows smoke honestly. Not a
   compliance tool and not a health prediction."

## (b) Claims we can and cannot make

| We can say | We cannot say |
|---|---|
| Plans keep paid hours and cut modeled hours at >=95F vs a fixed 05:30 start by 0.38 h/day (difference CI -0.43 to -0.33), and at >=80F by 1.22 h/day (EXPLORATORY, POST-HOC) | It beats heat-only planning on smoke (1 of 1296 days with fewer AQI>=101 hours than b3_late) |
| Smoke exposure is displayed next to every plan, with AQI and NowCast hours | It reduces smoke exposure (AQI>=101 difference -0.001, CI -0.007 to +0.005) |
| The evaluation was preregistered, with hashes, before the first real run | Any health outcome, illness reduction or "keeps workers safe" |
| Physical dominance vs B2 (W/T/L/mixed): 405/135/5/751 | Cal/OSHA compliance |
| Across 81 weight settings, the plan has no more >=95F or AQI>=101 hours than B2 on 99.3% of setting-days (strictly fewer on 31.3%) | Field microclimate accuracy (airport temperature, monitors 4.4 to 7.3 km away) |

## (c) Hardest judge questions

- **"Farms already start early."** Yes, and that is our toughest baseline. Against the fixed early start (B2,
  05:30) the plan still removes 0.38 h/day at >=95F (CI -0.43 to -0.33). Against a heat-only
  optimizer it adds nothing (ties on 1292 of 1296 days). So the value is in doing heat-first
  planning every day automatically, with smoke shown, not in a secret smoke advantage.
- **"Your metric isn't validated."** Correct. Modeled exposure-hours are a planning proxy, not a health
  outcome. We use Cal/OSHA trigger levels as thresholds, preregistered the analysis, checked the AQI
  breakpoints and NowCast against EPA's May 2026 technical document (matched), and report "mixed" days:
  747 of 751 mixed days differ only in hours >=80F, not in heat-for-smoke trades.
- **"Employers could misuse this."** It schedules shifts; it does not track workers. It keeps paid hours fixed
  by design, every output says it does not replace the written Heat Illness Prevention Plan, and water, shade
  and rest requirements still apply. The crew sheet is bilingual so workers see the same information.

## (d) Limitations

- Airport (ASOS) air temperature, not field temperature; no solar load (solar set to 0).
- PM2.5 monitors are 4.4 to 7.3 km from the weather stations.
- EPA AirData release status (preliminary or certified) is unverifiable from the listing.
- The forecast is a simple proxy (yesterday plus the 7-day mean), not a weather model.
- Cost weights are assumptions (see the weight-sensitivity table).
- Robust fell back on 224 real days that lacked enough history.
- No worker input: preferences, breaks, piece rates and travel were not modeled.
- Spanish text needs native-speaker review.
