# Madrugada pitch (template)

Numbers and verdict sentences in `{{...}}` come from eval/results.json (window 1, preregistered),
eval/results_w2.json (window 2, preregistered separately), and analysis/*.json (EXPLORATORY, POST-HOC: not
preregistered). Run `python -m analysis.fill_pitch` to write docs/PITCH_filled.md. Do not type numbers here.

## (a) 100-second demo script

1. (10 s) "Madrugada is a **heat-first shift planner with smoke exposure shown**. It places the same paid hours
   in the coolest allowed part of the day and puts the smoke picture next to the plan."
2. (15 s) Open the page on the default day **{{default_day}}** (picked by a stated rule: most observed
   dual-hazard hours). Point at the REAL and REPLAY badges and the threshold lines (80F, 95F, AQI 101, 151).
3. (15 s) Window 1 ({{w1_n}} region-days, {{w1_dates}} dates, 2022 to 2025): "With a 04:00 earliest start the plan
   cuts time at or above 95F by {{w1_heat_cut}} h/day vs a fixed 05:30 start (CI {{w1_heat_ci}})."
4. (15 s) Say where that comes from: "{{start_verdict}}"
5. (15 s) Window 2 ({{w2_n}} region-days, {{w2_dates}} dates, 2018 to 2021, preregistered before we fetched it):
   "{{w2_heat_sentence}} {{w2_smoke_sentence}}"
6. (10 s) "Smoke rarely moves the plan: {{smoke_why}}"
7. (10 s) Click "Print crew sheet": a bilingual summary with 12-hour times and the advisory disclaimer.
8. (10 s) Close: "An advisory aid that shows modeled heat and smoke exposure-hours honestly. Not a compliance
   tool and not a health prediction."

## (b) Claims we can and cannot make

| We can say | We cannot say |
|---|---|
| With a 04:00 earliest start, plans cut modeled hours at >=95F vs a fixed 05:30 start by {{w1_heat_cut}} h/day (window 1, CI {{w1_heat_ci}}); window 2: {{w2_heat_cut_text}} | That the planning logic beats simply starting at the earliest allowed time (it ties a fixed shift at that start on {{bsun_tie}} of {{w1_n}} days, EXPLORATORY) |
| Smoke exposure is shown next to every plan, with hourly AQI and NowCast hours | That it reduces smoke vs heat-only planning: {{w12_b3_smoke_text}} |
| Both windows were preregistered (with hashes) before their data were fetched or evaluated | Any heat benefit when the earliest start is 05:30 or sunrise-based: {{start_short}} |
| Physical dominance vs B2 (W/T/L/mixed): window 1 {{w1_phys_b2}}, window 2 {{w2_phys_b2}} | Any health outcome, illness reduction, "keeps workers safe", or Cal/OSHA compliance |
| Splitting the shift adds nothing measurable ({{two_block_share}} of days get two blocks, EXPLORATORY) | Field microclimate accuracy (airport temperature, monitors {{monitor_km}} km away) |

## (c) Hardest judge questions

- **"Farms already start early."** {{farms_answer}}
- **"Your metric isn't validated."** Correct: modeled exposure-hours are a planning proxy, not a health outcome.
  We used Cal/OSHA trigger levels as thresholds, preregistered two windows, checked the AQI breakpoints and
  NowCast against EPA's May 2026 document (they matched), and report "mixed" days: {{mixed_unchanged}} of
  {{mixed_total}} window-1 mixed days differ only in hours >=80F.
- **"Employers could misuse this."** It schedules shifts and tracks no one. Paid hours are fixed by design, every
  output says it does not replace the written Heat Illness Prevention Plan, and water, shade and rest rules
  still apply. The crew sheet is bilingual so workers see the same information.

## (d) Limitations

- The heat benefit assumes crews may start at 04:00, before dawn. That is a tunable assumption, not a legal limit.
- Airport (ASOS) air temperature, not field temperature; no solar load (solar set to 0).
- PM2.5 monitors are {{monitor_km}} km from the weather stations.
- Hourly PM2.5 values are scored against EPA's 24-hour AQI breakpoints. NowCast hours are shown as a secondary metric.
- EPA AirData release status (preliminary or certified) is unverifiable from the listing.
- The forecast is a simple proxy (yesterday plus the 7-day mean). Cost weights are assumptions.
- The robust planner fell back on {{robust_fallback}} window-1 days that lacked enough history.
- No worker input: preferences, breaks, piece rates and travel were not modeled.
- The Spanish crew-sheet text needs a native-speaker review (not yet done; the note stays on the sheet).
