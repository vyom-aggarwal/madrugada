# Madrugada: likely judge questions

Owners match the script: **A** problem and users · **B** data and testing · **C** results and limits · **D** app and build.
Keep answers to two or three sentences, then stop. Numbers come from the result files (start-time numbers are
EXPLORATORY, POST-HOC). If you don't know, say "we didn't test that" rather than guess.

## Innovation and idea (30%)
**1. How is this different from a weather app? (A)**
A weather app tells you it'll be 105°F. Madrugada turns that forecast into a shift plan with the same paid hours,
and then says which hot hours no start time can fix, so the crew lead knows when they need shade, rest or crew changes.

**2. What's actually new here? (C)**
We tested the idea honestly before selling it. Shifting hours helps only with a pre-dawn start, so the main readout is
the hours scheduling *can't* fix. Most planners promise an optimal schedule; ours also shows where scheduling stops helping.

**3. Why the name? (A)**
*Madrugada* is Spanish for the early hours before dawn: when crews can start, and the language many crews speak.

## Technical (25%)
**4. How does the optimizer work? (D)**
The day is 96 fifteen-minute slots, and each slot gets a cost from the heat and smoke thresholds. We search every
possible shift of one or two blocks, using prefix sums so it's instant. It's exhaustive, so it finds the true best plan
under the rules, and anyone can check it.

**5. Where does the forecast come from? (B)**
For each day, the plan uses only earlier days: half yesterday's profile plus half the average of the week before. That
keeps the test honest, with no peeking at the answer. A real deployment would plug in a weather-service forecast.

**6. How did you test it? (B)**
Real summers from airport weather stations and EPA air monitors: 1,296 region-days (2022–2025) and 768 more
(2018–2021), in Bakersfield, Fresno and Tulare. We wrote the rules down and hashed the code before each run, and the
confidence intervals resample whole dates because regions on the same day are correlated.

**7. What exactly did you find? (C)**
With a 4 AM earliest start, hours at or above 95°F drop by 0.38 a day versus a fixed 5:30 shift, in both windows
(CIs −0.43 to −0.33 and −0.44 to −0.32). With a 5:30 earliest start it's gone (+0.004 h/day). On smoke, there's no
benefit versus heat-only planning.

**8. 0.38 hours isn't much. Why does it matter? (C)**
It's about 23 minutes a day of the worst heat per crew, with paid hours unchanged. But we'd rather show the honest size
than inflate it, and that's why the app leads with the hours scheduling can't fix.

**9. Why no machine learning? (D)**
On purpose. Exhaustive search gives the provably best plan under the rules, and every number can be traced and checked.
For a tool about people's working conditions, being able to check it matters more than a black box.

**10. How do you know the code is right? (D)**
197 automated tests, including a claims audit that fails the build if our own text overclaims, plus
preregistration hashes so the evaluation code can't quietly change.

**11. Does it work without internet? (D)**
Yes. The app is one HTML page with no outside libraries or fonts, and it falls back to a built-in snapshot of 24 real
days if the server is unreachable. It's also deployed on Vercel.

## Design and UX (20%)
**12. Who is the user, and why this design? (A)**
A crew lead deciding the night before. So the first screen answers three things: when first light is, the best plan,
and what scheduling can't fix. Everything else is one tap away.

**13. What about workers who don't read English? (D)**
The crew sheet prints English and Spanish side by side on one page. We flag that the Spanish still needs a
native-speaker review before real use.

**14. Is it accessible? (D)**
Keyboard navigation, readable contrast in light and dark, reduced-motion support, and colour is never the only signal:
every badge and chart line also has text.

## Relevance and impact (15%)
**15. Who would use this tomorrow? (A)**
Crew leads, foremen and farm labor contractors in the Central Valley who set start times, and the crews who get the
printed sheet.

**16. Isn't starting at 4 AM its own risk? (C)**
Yes. Darkness, lighting and sleep matter. That's why the earliest start is an input the crew lead sets, not something
we push, and why the app shows the hours that remain when you start no earlier than first light.

**17. Could an employer use this to cut hours? (D)**
No. Paid hours are an input the tool holds constant, and it never proposes fewer. It also tracks no individual workers.

**18. Does this make crews compliant with Cal/OSHA? (C)**
No. It's an advisory planning aid in modeled exposure-hours. It doesn't replace the employer's written Heat Illness
Prevention Plan, and water, shade and rest requirements still apply.

**19. Why show smoke if scheduling doesn't help with it? (C)**
Because the smoke rule (AQI 151) brings its own requirements, so crew leads need to see it. We just don't claim
that moving hours fixes it.

## Limits and tough ones
**20. How accurate is the data for an actual field? (C)**
It's airport air temperature, not the field, with no sun load, and the air monitors are 4 to 22 km away. Those limits
are listed in the app's About sheet.

**21. Did you pick days that make it look good? (B)**
No. The evaluation uses every day with enough history. The demo day was picked by a stated rule (the real day with the
most observed heat-and-smoke hours) and is labeled that way on screen.

**22. Would a perfect forecast fix smoke? (B)**
Barely. Even planning with the day's actual data improves AQI 101+ hours versus the fixed shift by only 0.026 hours a
day in window 1. Smoke is mostly a whole-day problem, not a scheduling one.

**23. What would you do with more time? (A)**
A week with real crew leads, a native-speaker review of the Spanish, a real weather forecast, and field sensors
instead of airport data.

**24. Did you build all this today? (D)**
Yes. Everything was built during SierraHacks; the commit history shows it. We used Claude Code as an AI coding
assistant, and it's credited in our write-up.

**25. What was the hardest part? (B)**
Accepting the data. We set out to build a heat-and-smoke optimizer, found no smoke benefit, and rebuilt the story
around what the data actually supports.
