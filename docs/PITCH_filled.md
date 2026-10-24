# Madrugada pitch (filled from results; exploratory numbers are labeled EXPLORATORY, POST-HOC: not preregistered)

Numbers and verdict sentences in `{{...}}` come from eval/results.json (window 1, preregistered),
eval/results_w2.json (window 2, preregistered separately), and analysis/*.json (EXPLORATORY, POST-HOC: not
preregistered). Run `python -m analysis.fill_pitch` to write docs/PITCH_filled.md. Do not type numbers here.

## (a) 100-second demo script

1. (10 s) "Madrugada is a **heat-first shift planner with smoke exposure shown**. It places the same paid hours
   in the coolest allowed part of the day and puts the smoke picture next to the plan."
2. (15 s) Open the page on the default day **real-2024-07-14-bakersfield** (picked by a stated rule: most observed
   dual-hazard hours). Point at the REAL and REPLAY badges and the threshold lines (80F, 95F, AQI 101, 151).
3. (15 s) Window 1 (1296 region-days, 509 dates, 2022 to 2025): "With a 04:00 earliest start the plan
   cuts time at or above 95F by 0.38 h/day vs a fixed 05:30 start (CI -0.43 to -0.33)."
4. (15 s) Say where that comes from: "The benefit comes from the 04:00 earliest start, not from the planning: at a 05:30 earliest start it is +0.004 h/day (CI +0.001 to +0.008), and under a sunrise-minus-30-minutes rule +0.027 h/day (CI +0.012 to +0.042). It rests on the assumption that a crew may start at 04:00, before dawn."
5. (15 s) Window 2 (768 region-days, 431 dates, 2018 to 2021, preregistered before we fetched it):
   "Against B2 the plan changes hours at >=95F by -0.38 h/day (CI -0.44 to -0.32) and AQI>=101 hours by -0.046 (CI -0.076 to -0.017). For the optimizer, smoke avoidance did not change plans even in these years (188 region-days with any AQI>=101 hour, vs 109 in window 1): it ties b3_early on 729 of 768 days. The scenario-averaged (robust) variant does show a small reduction vs heat-only planning on its 522 non-fallback days: -0.036 h/day at AQI>=101 (CI -0.076 to -0.004), at +0.016 h/day at >=95F (CI +0.002 to +0.036)."
6. (10 s) "Smoke rarely moves the plan: in window 1 only 109 of 1296 region-days had any AQI>=101 hour, and the cleanest hours (16:00 to 18:00) are the hottest."
7. (10 s) Click "Print crew sheet": a bilingual summary with 12-hour times and the advisory disclaimer.
8. (10 s) Close: "An advisory aid that shows modeled heat and smoke exposure-hours honestly. Not a compliance
   tool and not a health prediction."

## (b) Claims we can and cannot make

| We can say | We cannot say |
|---|---|
| With a 04:00 earliest start, plans cut modeled hours at >=95F vs a fixed 05:30 start by 0.38 h/day (window 1, CI -0.43 to -0.33); window 2: -0.38 h/day (CI -0.44 to -0.32) | That the planning logic beats simply starting at the earliest allowed time (it ties a fixed shift at that start on 1290 of 1296 days, EXPLORATORY) |
| Smoke exposure is shown next to every plan, with hourly AQI and NowCast hours | That it reduces smoke vs heat-only planning: window 1: fewer AQI>=101 hours than b3_late on 1 of 1296 days; window 2: fewer than b3_late on 5 of 768 days |
| Both windows were preregistered (with hashes) before their data were fetched or evaluated | Any heat benefit when the earliest start is 05:30 or sunrise-based: at 05:30 +0.004 h/day (CI +0.001 to +0.008); sunrise rule +0.027 h/day (CI +0.012 to +0.042) |
| Physical dominance vs B2 (W/T/L/mixed): window 1 405/135/5/751, window 2 287/67/20/394 | Any health outcome, illness reduction, "keeps workers safe", or Cal/OSHA compliance |
| Splitting the shift adds nothing measurable (0.5% at 04:00 of days get two blocks, EXPLORATORY) | Field microclimate accuracy (airport temperature, monitors 4.4 to 22.4 km away) |

## (c) Hardest judge questions

- **"Farms already start early."** That is where our benefit disappears. Against a fixed 05:30 start, the plan cuts hours at >=95F only if crews may start earlier: with a 04:00 earliest start -0.377 h/day (CI -0.427 to -0.328), at 05:30 +0.004 h/day (CI +0.001 to +0.008), under a sunrise rule +0.027 h/day (CI +0.012 to +0.042). A fixed shift starting at the earliest allowed time ties the optimizer on 1290 of 1296 days (EXPLORATORY, POST-HOC). So the honest pitch is a daily, automatic heat-first schedule with smoke shown, not a smarter-than-early-start algorithm.
- **"Your metric isn't validated."** Correct: modeled exposure-hours are a planning proxy, not a health outcome.
  We used Cal/OSHA trigger levels as thresholds, preregistered two windows, checked the AQI breakpoints and
  NowCast against EPA's May 2026 document (they matched), and report "mixed" days: 747 of
  751 window-1 mixed days differ only in hours >=80F.
- **"Employers could misuse this."** It schedules shifts and tracks no one. Paid hours are fixed by design, every
  output says it does not replace the written Heat Illness Prevention Plan, and water, shade and rest rules
  still apply. The crew sheet is bilingual so workers see the same information.

## (d) Limitations

- The heat benefit assumes crews may start at 04:00, before dawn. That is a tunable assumption, not a legal limit.
- Airport (ASOS) air temperature, not field temperature; no solar load (solar set to 0).
- PM2.5 monitors are 4.4 to 22.4 km from the weather stations.
- Hourly PM2.5 values are scored against EPA's 24-hour AQI breakpoints. NowCast hours are shown as a secondary metric.
- EPA AirData release status (preliminary or certified) is unverifiable from the listing.
- The forecast is a simple proxy (yesterday plus the 7-day mean). Cost weights are assumptions.
- The robust planner fell back on 224 window-1 days that lacked enough history.
- No worker input: preferences, breaks, piece rates and travel were not modeled.
- The Spanish crew-sheet text needs a native-speaker review (not yet done; the note stays on the sheet).
