# Madrugada pitch (template)

Every number and verdict in `{{...}}` is read from eval/results.json (window 1, preregistered), eval/results_w2.json
(window 2, preregistered separately; never pooled) or the start-sensitivity data (EXPLORATORY, POST-HOC).
Run `python -m analysis.fill_pitch` to write docs/PITCH_filled.md. Do not type numbers here.

## (a) 100-second script

1. (10 s) "We tested whether shifting work hours reduces heat exposure for Central Valley crews, on real
   summers: window 1 ({{w1_n}} region-days, 2022 to 2025) and window 2 ({{w2_n}} region-days, 2018 to 2021). Each
   window was preregistered before its data were evaluated."
2. (15 s) "{{heat_verdict}}: vs a fixed 05:30 shift, {{w1_heat}} at or above 95F in window 1 and {{w2_heat}} in
   window 2 (modeled exposure-hours per day, 95% CI)."
3. (20 s) "At 05:30 or a sunrise-aligned start the benefit disappears. Window 1: 05:30 {{w1_0530}}, sunrise
   {{w1_sun}}. Window 2: 05:30 {{w2_0530}}, sunrise {{w2_sun}}. A fixed shift at the earliest allowed start ties
   the optimizer on {{bsun_tie}} of {{w1_n}} window-1 days." (EXPLORATORY)
4. (15 s) "Smoke: {{smoke_verdict}}"
5. (20 s) Open the planner on the default day. Read the **"Hours scheduling can't fix"** readout on screen: the hours
   at or above 95F that remain in the best plan starting no earlier than first light. "These hours need shade,
   rest or crew changes, not a different start time."
6. (10 s) Click "Print crew sheet": the same line, bilingual, labeled forecast-based estimate.
7. (10 s) Close: "An advisory day briefing in modeled exposure-hours. It does not replace the employer's written
   Heat Illness Prevention Plan."

## (b) Claims we can and cannot make

| We can say | We cannot say |
|---|---|
| With a 04:00 earliest start, modeled hours at or above 95F fall vs a fixed 05:30 shift: window 1 {{w1_heat}}, window 2 {{w2_heat}} | That shifting hours helps when crews cannot start before dawn (05:30: window 1 {{w1_0530}}, window 2 {{w2_0530}}) |
| The optimizer nearly always picks the same plan as heat-only planning (ties b3_early on {{w1_b3_tie}} of {{w1_n}} and {{w2_b3_tie}} of {{w2_n}} days) | That it reduces smoke vs heat-only planning (AQI>=101 vs b3_early: window 1 {{w1_b3_smoke}}, window 2 {{w2_b3_smoke}}) |
| In window 2, AQI>=101 hours fall slightly vs the early fixed shift ({{w2_smoke_b2}}) | Any pooled two-window number, or any result without its window label |
| Both windows were preregistered with code and config hashes before evaluation | Any safety, health-outcome or legal-compliance claim |
| The readout shows the high-heat hours that no start time after first light removes | Field microclimate accuracy (airport temperature; monitors up to {{max_km}} km away) |

## (c) Hardest judge questions

- **"Farms already start early."** Yes, and against a 05:30 start our scheduling adds nothing on heat: window 1
  {{w1_0530}}, window 2 {{w2_0530}} at or above 95F. The heat benefit ({{w1_heat}} in window 1) exists only if a
  crew may start at 04:00, before dawn. That is why the product leads with the hours scheduling can't fix.
- **"Your metric isn't validated."** Correct. Modeled exposure-hours are a planning proxy built on Cal/OSHA trigger
  levels, not a health outcome. We preregistered both windows, report each with its own date-cluster CI
  ({{w1_dates}} and {{w2_dates}} distinct dates; region-days are not the effective sample size), and report
  "mixed" days instead of hiding them (window 1 physical W/T/L/mixed vs B2: {{w1_phys}}).
- **"Employers could squeeze hours."** Paid hours are an input the tool holds constant; it never proposes fewer
  paid hours. The optimizer rarely splits the shift ({{two_block}} of window-1 days at 04:00, EXPLORATORY). It
  tracks no workers, and its main output is the high-heat time no start time removes, which points to shade, rest
  and crew changes.

## (d) Limitations

- Airport (ASOS) air temperature, not field temperature; no solar load.
- Monitor distance: {{tulare_note}}. {{excluded_note}}.
- The forecast is a simple proxy (yesterday plus the 7-day mean), not a weather model.
- Cost weights and levels are assumptions.
- PM2.5 AQI breakpoints are marked unverified in config (a later read-only check matched EPA's May 2026 document).
  Hourly values are scored against 24-hour breakpoints.
- EPA AirData release status (preliminary or certified) is unverifiable from the listing.
- No worker input: preferences, breaks, piece rates and travel were not modeled.
- The Spanish text needs a native-speaker review.
