# Madrugada: Devpost submission (copy and paste)

Every number below comes from the result files (`eval/results.json`, `eval/results_w2.json`) or the app's
default day (Bakersfield, 2024-07-14, a recorded real day). Start-time numbers are EXPLORATORY, POST-HOC.

---

## General info

**Project name:** `Madrugada`

**Elevator pitch** (158 of 200 characters):
```
Heat-first shift planner for Central Valley farm crews: same paid hours, a smarter start time, and an honest count of the high-heat hours no schedule can fix.
```

---

## About the project (paste into the Markdown box)

```markdown
## Inspiration
In a Central Valley summer, high heat and wildfire smoke can land on the same day, and a crew lead has to pick tomorrow's start time tonight. Cal/OSHA rules switch on at thresholds (80°F shade, 95°F high-heat procedures, AQI 151 for the wildfire smoke rule), but a threshold only tells you when you've crossed a line. It doesn't help you rebuild the shift. *Madrugada* is Spanish for the hours before dawn, and we wanted to know: does moving work earlier actually reduce time in the worst heat, and by how much?

## What it does
Madrugada is a day briefing for **crew leads, foremen and farm labor contractors**:
- **Today:** first light, the best work plan that starts no earlier than first light, and forecast temperature and air quality against the Cal/OSHA trigger lines, for a recorded real day (every day carries a REAL or SYNTHETIC badge, and a REPLAY label).
- **Planner:** paid hours are an input the tool holds constant. It compares our plan with a fixed 7:00 shift, a fixed 5:30 shift and a heat-only planner, in modeled exposure-hours.
- **The hours scheduling can't fix:** the high-heat hours left even in the best plan from first light. On the default day that's 3.5 modeled hours at or above 95°F. Those hours need shade, rest or crew changes, not a different start time.
- **Crew sheet:** a one-page, English and Spanish printable sheet with the plan and that line.
- **Evidence:** our preregistered results, each with its own confidence interval.
- A narrated opening sequence (with a presenter mode) tells the story with numbers read live from the result files.

It's an advisory aid in modeled exposure-hours. It isn't a compliance tool or a health prediction, it doesn't replace the employer's written Cal/OSHA Heat Illness Prevention Plan, and it tracks no individual workers.

## How we built it
- **Backend:** Python, FastAPI and numpy. The day is a grid of 96 fifteen-minute slots. Each slot gets a cost from config-file thresholds:

$$ c_s = w_h\,h(T_s) + w_m\,m(\mathrm{AQI}_s) + w_d\,\mathbf{1}[\text{dual hazard}] $$

  and the optimizer does an **exhaustive search** over every shift of one or two blocks using prefix sums. No solver and no machine learning, so every answer can be checked.
- **Forecast without peeking:** the plan for day \\( D \\) uses only earlier days, \\( \hat{x}_D = 0.5\,x_{D-1} + 0.5\,\bar{x}_{D-7..D-1} \\). An ORACLE mode that uses the day's own data is labeled as an upper bound everywhere.
- **Real data, no API keys:** IEM ASOS airport weather and EPA AirData PM2.5, converted to local clock time. PurpleAir readings can be corrected with the EPA US-wide formula \\( 0.524\,\mathrm{PM}_{cf1} - 0.0862\,\mathrm{RH} + 5.75 \\).
- **Evaluation:** two windows of real summers, **1,296 region-days (2022–2025)** and **768 region-days (2018–2021)**. Each was **preregistered** with SHA-256 hashes of the code and config before it ran. Confidence intervals use a bootstrap that resamples whole dates, and the two windows are never pooled.
- **Frontend:** one offline HTML file with vanilla JavaScript, inline SVG charts and a canvas opening sequence. It has light and dark themes, works from phone to desktop, and needs no build step or CDN.
- **Guardrails:** 184 automated tests, including a claims audit that fails the build if our own text overclaims.

## Challenges we ran into
- **The data said no on smoke.** We started out building a dual heat-and-smoke optimizer. On real data it showed no smoke benefit over heat-only planning, so we repositioned it as a heat-first planner that *shows* smoke, and said so.
- **The benefit depends on the start time.** With a 4:00 AM earliest start, modeled hours at or above 95°F fell by **0.38 h/day** versus a fixed 5:30 shift (window 1 CI −0.43 to −0.33; window 2 −0.38, CI −0.44 to −0.32). With a 5:30 earliest start it disappears (window 1 +0.004 h/day, CI +0.001 to +0.008). That changed the product: it now leads with the hours scheduling can't fix.
- **Getting real data without keys:** time zones and daylight time, monitors several kilometres from the weather stations, and missing days.
- **Honesty under time pressure:** we kept every number tied to a result file and wrote a test that blocks words like "guarantees".

## Accomplishments that we're proud of
- Two preregistered real-data evaluations, with the result replicated in both windows.
- An honest product turn: the main readout is what scheduling *can't* fix.
- A polished offline app with a bilingual crew sheet and a narrated opening sequence.
- 184 passing tests, and every number on screen read from the results at runtime.

## What we learned
Write the evaluation rules down before you look at the results. A negative result can make a better product. And region-days on the same date aren't independent, so the confidence intervals have to resample dates.

## What's next for Madrugada
- A native-speaker review of the Spanish crew sheet.
- A week of use with real crew leads, and their input on breaks, travel and piece rates.
- Field sensors instead of airport weather.

*Built during SierraHacks 2026. Weather data: Iowa Environmental Mesonet (IEM ASOS). PM2.5: U.S. EPA AirData. PurpleAir correction: Barkjohn et al. 2021 (EPA). Code written with help from Claude Code (AI coding assistant).*
```

---

## Built with (tags; type each and press Enter)
`python` · `fastapi` · `uvicorn` · `pydantic` · `numpy` · `pandas` · `pytest` · `javascript` · `html5` · `css3` ·
`svg` · `canvas` · `node.js` · `iem-asos` · `epa-airdata` · `claude-code`

## "Try it out" links
- GitHub: https://github.com/vyom-aggarwal/madrugada (make sure the repository is **public**)
- Optional: the pitch deck link, once it's shared from the deck's Share menu.

## Image gallery (upload in this order; all 1500×1000 px, 3:2, under 5 MB)
Files are in the `submission/` folder:
1. `01-intro-idea.png`: the logo and "same paid hours, different clock" (best thumbnail)
2. `02-intro-problem.png`: the forecast against the Cal/OSHA trigger lines
3. `03-intro-test.png`: the start-time dial with its confidence interval
4. `04-intro-cant-fix.png`: the hours scheduling can't fix
5. `05-today.png`: Today briefing (light)
6. `06-today-dark.png`: Today briefing (dark)
7. `07-planner.png`: Planner: before and after, with paid hours held constant
8. `08-evidence.png`: Evidence: the preregistered findings
9. `09-crew-sheet.png`: the bilingual crew sheet

## Video demo link
Record the narrated walkthrough in `docs/PITCH_SCRIPT.md` (4 presenters, about 2¾ minutes):
1. Run `python tasks.py demo` and open `http://127.0.0.1:8000/static/index.html?present=1`, full screen (F11).
2. Record the screen with audio (Windows: Win+Alt+R with the Xbox Game Bar, or OBS). Use `?intro=0` for retakes
   that start in the app.
3. Upload to YouTube as **Unlisted** (or Vimeo) and paste the link into "Video demo link".
