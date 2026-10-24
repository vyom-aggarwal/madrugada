# Madrugada: narrated demo script (4 presenters, about 2½ minutes)

Replace **A–D** with your names. Every number is one the app shows on screen.

**Setup:** run `python tasks.py demo`, open `http://127.0.0.1:8000/static/index.html?present=1`, press F11.
Each intro scene waits for you. **Next:** click, Space, → or a clicker. **Back:** ←. **Esc:** straight into the app.
If anything breaks, open `?intro=0` and keep going.

| Who | Scenes | Time |
|---|---|---|
| A | 1–2 · the problem | 0:00–0:30 |
| B | 3–4 · the idea and the test | 0:30–1:10 |
| C | 5–6 · what we found | 1:10–1:40 |
| D | live app and close | 1:40–2:30 |

---

**A, scene 1:** "Hi, we're [team]. It's 4 AM in the Central Valley, and a crew boss has to pick tomorrow's start time." *[Next]*

**A, scene 2:** "Heat and smoke rules switch on at thresholds: 80 degrees, 95, AQI 151. They tell you when you've crossed a line, not how to plan the shift." *[Next]*

**B, scene 3:** "Madrugada means the hours before dawn. Same paid hours, earlier clock: here, 7 to 3:30 becomes 4 to 12:30." *[Next]*

**B, scene 4:** "We tested it on real summers, 1,296 and 768 region-days, with our rules locked in before we looked. Starting at 4 cuts high-heat time. Watch the dial: by 6, the benefit is gone." *[Next]*

**C, scene 5:** "So the app leads with what scheduling *can't* fix. Today, even starting at first light, 3.5 hours are above 95. Those need shade, rest or crew changes." *[Next]*

**C, scene 6:** "It's modeled exposure-hours and an advisory aid. It doesn't replace the employer's Cal/OSHA plan. D?" *[Next]*

**D, in the app:**
- **Today:** "First light, the best plan, and the hours scheduling can't fix, all on real recorded data."
- **Make crew sheet:** "One printed page in English and Spanish for the crew."
- **Close:** "Madrugada: same hours, smarter dawn. Thank you!"

---

**Q&A cheat sheet**
- *Farms already start early?* (B) Right. Against a 5:30 start we add nothing on heat, so the app leads with what scheduling can't fix.
- *Smoke?* (C) No benefit versus heat-only planning, and we say so.
- *Safety or compliance tool?* (C) No. It's an advisory aid in modeled exposure-hours.
- *Fewer paid hours?* (D) Never. Paid hours are held constant, and no workers are tracked.
- *AI?* (A) No machine learning by design: it checks every possible shift, so every answer is checkable.
