# Madrugada: narrated demo script (4 presenters, about 4 minutes)

Replace **A**, **B**, **C** and **D** with your names. Every number below matches what the app shows on screen
(window 1, window 2 and start-time results come from the result files; the default day is Bakersfield,
2024-07-14, a recorded real day). Start-time numbers are EXPLORATORY, POST-HOC: not preregistered.

## Before you go on
- Start the server: `python tasks.py demo`, then open **`http://127.0.0.1:8000/static/index.html?present=1`**.
  Offline backup: add `&snapshot` (sliders and the crew sheet are off in snapshot mode).
- Presenter mode waits at the end of every scene. **Next**: click, Space, Enter, → or Page Down (a clicker
  works). **Back**: ← or Page Up. **Esc** jumps straight into the app.
- Full-screen the browser (F11). Close other tabs. Turn notifications off.
- If anything misbehaves, open `?intro=0` to go straight to the app and keep talking.
- Rule for everyone: say "modeled exposure-hours", never promise health or legal outcomes.

| Who | Part | Scenes | Time |
|---|---|---|---|
| A | The problem and who it's for | 1–2 | 0:00–0:50 |
| B | The idea and how we tested it | 3–4 | 0:50–1:50 |
| C | What we found, honestly | 5–7 | 1:50–3:00 |
| D | Live demo and close | the app | 3:00–4:10 |

---

## A: The problem (scenes 1–2)

**Scene 1, cold open** (wait for the line to finish typing)
> Hi, we're [team name]. I'm A. It's four in the morning in the Central Valley. A crew boss has to decide
> when tomorrow's shift starts, before the heat, and before anyone knows what the air will be like.

*[Next]*

**Scene 2, the problem** (the lines draw in while you talk)
> In summer, heat and wildfire smoke can land on the same day. Cal/OSHA rules switch on at thresholds:
> 80 degrees means shade, 95 means high-heat procedures, and an AQI of 151 triggers the wildfire smoke
> rule. This is a recorded day in Bakersfield. The rules tell you when you've crossed a line. They don't
> help you rebuild the shift. That's what we built Madrugada for: crew leads, foremen and labor contractors
> who set tomorrow's start time. B will show you the idea.

*[Next]*

## B: The idea and the test (scenes 3–4)

**Scene 3, the idea**
> Madrugada is Spanish for the hours before dawn. The idea is simple: same paid hours, different clock.
> On this day, our planner moves the usual 7 AM to 3:30 PM shift to 4 AM to 12:30 PM. Still eight and a
> half paid hours. It never cuts pay to dodge heat.

*[Next]*

**Scene 4, the test** (let the dial sweep before you give the takeaway)
> We didn't want to just claim this works, so we tested it on real summers: 1,296 region-days from 2022
> to 2025, and 768 from 2018 to 2021, using airport weather and EPA air monitors. Before each run we wrote
> the rules down and locked the code with hashes, so we couldn't tune it after seeing results.
> Now watch the dial. As the earliest allowed start moves later, the benefit shrinks. By 6 AM the plan
> has slightly *more* high-heat hours than a fixed 5:30 shift. That sweep is exploratory.
> C will tell you what that means.

*[Next]*

## C: What we found (scenes 5–7)

**Scene 5, the honest part** (one beat at a time, as each line appears)
> Here's the honest answer. Shifting hours cuts high-heat time only if crews can start before dawn. With
> a 4 AM start allowed, modeled hours at or above 95 drop by about 0.38 hours a day versus a fixed 5:30
> shift.
> And it replicated: both preregistered windows show the same drop, each with its own confidence interval.
> On smoke, there's a small reduction versus the early fixed shift in window 2 only, and none versus
> heat-only planning. So we call Madrugada a heat-first planner that shows smoke exposure.

*[Next]*

**Scene 6, what scheduling can't fix**
> That result changed what the app leads with. On this day, even the best plan that starts at first light,
> 5:15 AM, still has 3.5 modeled hours at or above 95 degrees. No start time fixes those. They need shade,
> rest or crew changes, and the app says so on the first screen and on the crew sheet.

*[Next]*

**Scene 7, limits** (a quiet beat; slow down)
> To be clear about limits: these are modeled exposure-hours from airport weather and nearby monitors,
> with no worker input yet. It's an advisory aid. It doesn't replace the employer's written Cal/OSHA
> heat plan. D will show you the app.

*[Next: the intro opens into the app]*

## D: Live demo and close (in the app)

1. **Today tab** (20 s)
   > This is the briefing a crew lead sees. The badges say this is real recorded data, replayed, not live.
   > First light, the best plan from first light, and the day at a glance.

   Hover the ribbon chart to show temperature and air quality at any time, then point at the last tile:
   > And here's the number scheduling can't fix.
2. **Planner tab** (20 s)
   Drag **Paid hours**.
   > Paid hours are an input we hold constant. Here's our plan next to the fixed 7 AM and 5:30 shifts and a
   > heat-only planner, in modeled hours at each threshold.
3. **Evidence tab** (10 s)
   > Every number in the pitch comes from here: both preregistered windows, each with its own interval.
4. **Make crew sheet** (Today tab; 15 s)
   > One printed page, English and Spanish side by side, with the plan and the hours it can't fix. The
   > Spanish still needs a native-speaker review.
5. **Close** (5 s)
   > Madrugada: same hours, smarter dawn. Thank you. We'd love your questions.

---

## Q&A: who answers what
| Question | Who | Short answer |
|---|---|---|
| "Farms already start early." | B | Right, and against a 05:30 start our scheduling adds nothing on heat. The benefit needs a 04:00 start, which is why the app leads with the hours scheduling can't fix. |
| "How do you know it works?" | B | Two preregistered real-data windows, hashed code, confidence intervals that resample whole dates, and the "mixed" days reported, not hidden. |
| "Is this a safety or compliance tool?" | C | No. It's an advisory aid in modeled exposure-hours, not a health prediction. It doesn't replace the written Cal/OSHA plan. |
| "What about smoke?" | C | Small reduction vs the early fixed shift in window 2; none vs heat-only planning. We show smoke, we don't claim to beat heat-only planning on it. |
| "Could employers use it to squeeze hours?" | D | Paid hours are held constant; it never proposes fewer. It tracks no individual workers. |
| "How accurate is the weather?" | C | Airport temperature, not the field; monitors up to about 22 km away; a simple forecast. All listed in the About sheet. |
| "What's next?" | D | Native-speaker review of the Spanish, a week with real crew leads, field sensors. |
| "Is there AI?" | A | No machine learning by design: an exhaustive search over every possible shift, so every result can be checked. |

## Rehearsal notes
- Run it twice with a timer. If you're long, trim D's Planner step first.
- The intro waits for you, so finish each sentence before you click.
- Hand-offs ("B will show you…") are part of the script: they keep the 10% presentation score smooth.
