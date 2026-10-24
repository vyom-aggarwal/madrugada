# Madrugada pitch (filled from the result files; start-time numbers are EXPLORATORY, POST-HOC: not preregistered)

Every number and verdict in `{{...}}` is read from eval/results.json (window 1, preregistered), eval/results_w2.json
(window 2, preregistered separately; never pooled) or the start-sensitivity data (EXPLORATORY, POST-HOC).
Run `python -m analysis.fill_pitch` to write docs/PITCH_filled.md. Do not type numbers here.

## (a) 100-second script

1. (10 s) "We tested whether shifting work hours reduces heat exposure for Central Valley crews, on real
   summers: window 1 (1296 region-days, 2022 to 2025) and window 2 (768 region-days, 2018 to 2021). Each
   window was preregistered before its data were evaluated."
2. (15 s) "Shifting hours reduces heat exposure only if crews can start before dawn (04:00): vs a fixed 05:30 shift, -0.38 h/day (CI -0.43 to -0.33) at or above 95F in window 1 and -0.38 h/day (CI -0.44 to -0.32) in
   window 2 (modeled exposure-hours per day, 95% CI)."
3. (20 s) "At 05:30 or a sunrise-aligned start the benefit disappears. Window 1: 05:30 +0.004 h/day (CI +0.001 to +0.008), sunrise
   +0.027 h/day (CI +0.012 to +0.042). Window 2: 05:30 +0.022 h/day (CI +0.010 to +0.036), sunrise +0.046 h/day (CI +0.022 to +0.070). A fixed shift at the earliest allowed start ties
   the optimizer on 1290 of 1296 window-1 days." (EXPLORATORY)
4. (15 s) "Smoke: a small reduction vs the early fixed shift in window 2, -0.046 h/day (CI -0.076 to -0.017); none vs heat-only planning (AQI>=101 vs b3_early: window 1 +0.000 h/day (CI +0.000 to +0.000), window 2 -0.005 h/day (CI -0.031 to +0.016))."
5. (20 s) Open the planner on the default day. Read the **"Hours scheduling can't fix"** readout on screen: the hours
   at or above 95F that remain in the best plan starting no earlier than first light. "These hours need shade,
   rest or crew changes, not a different start time."
6. (10 s) Click "Print crew sheet": the same line, bilingual, labeled forecast-based estimate.
7. (10 s) Close: "An advisory day briefing in modeled exposure-hours. It does not replace the employer's written
   Heat Illness Prevention Plan."

## (b) Claims we can and cannot make

| We can say | We cannot say |
|---|---|
| With a 04:00 earliest start, modeled hours at or above 95F fall vs a fixed 05:30 shift: window 1 -0.38 h/day (CI -0.43 to -0.33), window 2 -0.38 h/day (CI -0.44 to -0.32) | That shifting hours helps when crews cannot start before dawn (05:30: window 1 +0.004 h/day (CI +0.001 to +0.008), window 2 +0.022 h/day (CI +0.010 to +0.036)) |
| The optimizer nearly always picks the same plan as heat-only planning (ties b3_early on 1292 of 1296 and 729 of 768 days) | That it reduces smoke vs heat-only planning (AQI>=101 vs b3_early: window 1 +0.000 h/day (CI +0.000 to +0.000), window 2 -0.005 h/day (CI -0.031 to +0.016)) |
| In window 2, AQI>=101 hours fall slightly vs the early fixed shift (-0.046 h/day (CI -0.076 to -0.017)) | Any pooled two-window number, or any result without its window label |
| Both windows were preregistered with code and config hashes before evaluation | Any safety, health-outcome or legal-compliance claim |
| The readout shows the high-heat hours that no start time after first light removes | Field microclimate accuracy (airport temperature; monitors up to 22.45 km away) |

## (c) Hardest judge questions

- **"Farms already start early."** Yes, and against a 05:30 start our scheduling adds nothing on heat: window 1
  +0.004 h/day (CI +0.001 to +0.008), window 2 +0.022 h/day (CI +0.010 to +0.036) at or above 95F. The heat benefit (-0.38 h/day (CI -0.43 to -0.33) in window 1) exists only if a
  crew may start at 04:00, before dawn. That is why the product leads with the hours scheduling can't fix.
- **"Your metric isn't validated."** Correct. Modeled exposure-hours are a planning proxy built on Cal/OSHA trigger
  levels, not a health outcome. We preregistered both windows, report each with its own date-cluster CI
  (509 and 431 distinct dates; region-days are not the effective sample size), and report
  "mixed" days instead of hiding them (window 1 physical W/T/L/mixed vs B2: 405/135/5/751).
- **"Employers could squeeze hours."** Paid hours are an input the tool holds constant; it never proposes fewer
  paid hours. The optimizer rarely splits the shift (0.5% of window-1 days at 04:00, EXPLORATORY). It
  tracks no workers, and its main output is the high-heat time no start time removes, which points to shade, rest
  and crew changes.

## (d) Limitations

- Airport (ASOS) air temperature, not field temperature; no solar load.
- Monitor distance: PM2.5 monitors are 4.39 to 22.45 km from the weather stations; the farthest is Tulare in 2018-2020 (window 2). Bakersfield 2018-2020 excluded in window 2 (no active PM2.5 monitor within 25 km).
- The forecast is a simple proxy (yesterday plus the 7-day mean), not a weather model.
- Cost weights and levels are assumptions.
- PM2.5 AQI breakpoints are marked unverified in config (a later read-only check matched EPA's May 2026 document).
  Hourly values are scored against 24-hour breakpoints.
- EPA AirData release status (preliminary or certified) is unverifiable from the listing.
- No worker input: preferences, breaks, piece rates and travel were not modeled.
- The Spanish text needs a native-speaker review.
