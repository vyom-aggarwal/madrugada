# Madrugada pitch (template)

Numbers in `{{...}}` come from eval/results.json (preregistered) and analysis/exploratory_results.json
(EXPLORATORY, POST-HOC: not preregistered). Run `python -m analysis.fill_pitch` to write docs/PITCH_filled.md.
Do not type numbers into this file.

## (a) 100-second demo script

1. (10 s) "Madrugada is a **heat-first shift planner with smoke exposure shown**. For a Central Valley crew it
   moves the same paid hours into the coolest part of the day and shows the smoke picture next to it."
2. (15 s) Open the page on the default day **{{default_day}}** (picked by a stated rule: most observed
   dual-hazard hours). Point at the REAL and REPLAY badges and the dashed lines: 80F shade trigger, 95F
   high-heat procedures, AQI 101 and 151.
3. (15 s) Comparison table: the optimizer vs the fixed shifts B1 and B2 and the heat-only planner B3.
   Toggle "observed".
4. (15 s) Backtest headline: "On {{real_n}} real region-days ({{real_dates}} dates, summers 2022 to 2025), the
   plan cut time at or above 95F by **{{heat95_cut}} h/day** vs a fixed 05:30 start (95% CI {{heat95_ci}})."
5. (15 s) Say the limit out loud: "There was **no measurable smoke benefit** ({{smoke_mean}} h/day, CI
   {{smoke_ci}}). It ties heat-only planning on {{b3e_tie}} of {{real_n}} days. Even with perfect hindsight the
   oracle changes smoke hours by only {{oracle_smoke}} h/day."
6. (10 s) Why: "Smoke was rare ({{days_aqi101}} of {{real_n}} days had any AQI>=101 hour), and the cleanest hours
   are late afternoon ({{cleanest}}), when it is hottest. The coolest hours ({{coolest}}) are not the cleanest."
7. (10 s) Click "Print crew sheet": a bilingual summary with 12-hour times and the advisory disclaimer.
8. (10 s) Close: "An advisory aid that reduces modeled heat exposure-hours and shows smoke honestly. Not a
   compliance tool and not a health prediction."

## (b) Claims we can and cannot make

| We can say | We cannot say |
|---|---|
| Plans keep paid hours and cut modeled hours at >=95F vs a fixed 05:30 start by {{heat95_cut}} h/day (difference CI {{heat95_ci}}), and at >=80F by {{heat80_cut}} h/day (EXPLORATORY, POST-HOC) | It beats heat-only planning on smoke ({{b3_smoke_wins}} of {{real_n}} days with fewer AQI>=101 hours than b3_late) |
| Smoke exposure is displayed next to every plan, with AQI and NowCast hours | It reduces smoke exposure (AQI>=101 difference {{smoke_mean}}, CI {{smoke_ci}}) |
| The evaluation was preregistered, with hashes, before the first real run | Any health outcome, illness reduction or "keeps workers safe" |
| Physical dominance vs B2 (W/T/L/mixed): {{phys_b2}} | Cal/OSHA compliance |
| Across 81 weight settings, the plan has no more >=95F or AQI>=101 hours than B2 on {{weak_day}} of setting-days (strictly fewer on {{strict_day}}) | Field microclimate accuracy (airport temperature, monitors {{monitor_km}} km away) |

## (c) Hardest judge questions

- **"Farms already start early."** Yes, and that is our toughest baseline. Against the fixed early start (B2,
  05:30) the plan still removes {{heat95_cut}} h/day at >=95F (CI {{heat95_ci}}). Against a heat-only
  optimizer it adds nothing (ties on {{b3e_tie}} of {{real_n}} days). So the value is in doing heat-first
  planning every day automatically, with smoke shown, not in a secret smoke advantage.
- **"Your metric isn't validated."** Correct. Modeled exposure-hours are a planning proxy, not a health
  outcome. We use Cal/OSHA trigger levels as thresholds, preregistered the analysis, checked the AQI
  breakpoints and NowCast against EPA's May 2026 technical document (matched), and report "mixed" days:
  {{mixed_unchanged}} of {{mixed_total}} mixed days differ only in hours >=80F, not in heat-for-smoke trades.
- **"Employers could misuse this."** It schedules shifts; it does not track workers. It keeps paid hours fixed
  by design, every output says it does not replace the written Heat Illness Prevention Plan, and water, shade
  and rest requirements still apply. The crew sheet is bilingual so workers see the same information.

## (d) Limitations

- Airport (ASOS) air temperature, not field temperature; no solar load (solar set to 0).
- PM2.5 monitors are {{monitor_km}} km from the weather stations.
- EPA AirData release status (preliminary or certified) is unverifiable from the listing.
- The forecast is a simple proxy (yesterday plus the 7-day mean), not a weather model.
- Cost weights are assumptions (see the weight-sensitivity table).
- Robust fell back on {{robust_fallback}} real days that lacked enough history.
- No worker input: preferences, breaks, piece rates and travel were not modeled.
- Spanish text needs native-speaker review.
