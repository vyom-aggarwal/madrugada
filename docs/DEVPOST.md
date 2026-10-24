# Madrugada: SierraHacks 2026 submission kit

Main track (agriculture in the Central Valley). Every number below is copied from `docs/PITCH_filled.md`,
which is filled from the result files. Start-time numbers are EXPLORATORY, POST-HOC: not preregistered.

## Submission checklist (Devpost needs all four)
- [ ] **Screenshots** (light and dark, phone and desktop): Today tab with the hero and ribbon, Planner with the
      comparison table, Evidence tab, the printed crew sheet, the About sheet ("Who it helps").
- [ ] **Link**: the repository URL (the app runs offline with `python tasks.py demo`).
- [ ] **Slides**: the Madrugada pitch deck (export as PDF or PPTX from the deck's Share menu).
- [ ] **Demo video**: the narrated script in `docs/PITCH_SCRIPT.md`.

## Devpost text

**Tagline:** Same hours. Smarter dawn. A heat-first shift planner for Central Valley farm crews, with smoke shown.

**Inspiration.** In a Central Valley summer, high heat and wildfire smoke can land on the same day, and someone
has to pick tomorrow's start time tonight. We wanted to know whether moving work hours actually changes heat
exposure, and to show the answer honestly.

**What it does.** Pick a place and a recorded summer day. Madrugada shows forecast temperature and air quality
against Cal/OSHA trigger lines (80°F shade, 95°F high heat, AQI 151 wildfire smoke rule), the best work plan that
starts no earlier than first light with paid hours held constant, and the **hours scheduling can't fix**: the
high-heat hours left even in that best plan, which need shade, rest or crew changes. It prints a one-page
English/Spanish crew sheet.

**Who it helps.** Crew leads, foremen and farm labor contractors who set start times, and the crews who get the
plan on paper. It tracks no individual workers.

**How we built it.** FastAPI and numpy. The optimizer tries every one- or two-block shift on a 15-minute grid
(prefix sums, no black box). The forecast uses only past days (yesterday plus the prior 7-day mean). Real data
comes keyless from IEM ASOS airport weather and EPA AirData PM2.5. The front end is one offline HTML file with
inline SVG charts. 176 automated tests, including a claims audit that fails on overclaiming words.

**What we found.** We preregistered two windows of real summers (1,296 region-days, 2022 to 2025; 768
region-days, 2018 to 2021) and locked code hashes before each evaluation. If crews may start at 04:00, modeled
hours at or above 95°F fall vs a fixed 05:30 shift: window 1 -0.38 h/day (CI -0.43 to -0.33), window 2 -0.38
h/day (CI -0.44 to -0.32). With an earliest start of 05:30 the benefit disappears (exploratory). Smoke: no
difference vs heat-only planning. That is why the app leads with the hours scheduling can't fix.

**Challenges.** Not overclaiming. Our first idea was a dual-hazard optimizer; the real data showed no smoke
benefit over heat-only planning, so we changed the product to match the evidence.

**Accomplishments.** Two preregistered real-data evaluations, a working offline app, and a bilingual print sheet.

**What we learned.** Write the evaluation rules down before looking at the results.

**What's next.** A native-speaker review of the Spanish, a week of use with crew leads, field sensors.

**Built with:** Python, FastAPI, numpy, pandas, pydantic, pytest, vanilla JavaScript, SVG.
**Credits:** IEM ASOS (Iowa Environmental Mesonet), U.S. EPA AirData, Barkjohn et al. 2021 (EPA PurpleAir
correction). Code written with help from Claude Code (AI coding assistant).

**Limits.** Advisory planning aid in modeled exposure-hours. Not a compliance tool and not a health prediction.
It does not replace the employer's written Cal/OSHA Heat Illness Prevention Plan; water, shade and rest
requirements still apply.

## Demo video
Record the narrated walkthrough in `docs/PITCH_SCRIPT.md` (4 presenters, about 4 minutes). Open the app with
`?present=1` so each intro scene waits for the narrator; use `?intro=0` for retakes that start in the app.
