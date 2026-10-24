"""Pre-registration for WINDOW 2 (summers 2018 to 2021). Non-logic. Writes eval/PREREGISTRATION_2.md with the same
hash lines as eval/PREREGISTRATION.md (verified equal before writing), so eval.prereg.verify() can check it.

Run: python -m analysis.prereg2 write   |   python -m analysis.prereg2   (verify only)
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import load_config  # noqa: E402
from eval import prereg  # noqa: E402

PREREG2 = ROOT / "eval" / "PREREGISTRATION_2.md"
YEARS = [2018, 2019, 2020, 2021]
CACHE_W2 = "data/cache_w2/"


def recorded(path: Path) -> dict:
    return {m.group(2): m.group(1) for m in map(prereg.LINE.match, path.read_text(encoding="utf-8").splitlines()) if m}


def check_equal() -> list[str]:
    """Current hashes must equal those frozen in eval/PREREGISTRATION.md (window 1)."""
    w1, now = recorded(prereg.PREREG_PATH), prereg.current_hashes()
    return [f"{k}: differs from PREREGISTRATION.md" for k in now if w1.get(k) != now[k]]


def render(today: str | None = None) -> str:
    cfg = load_config()
    j, e, k = cfg["real_job"], cfg["eval"], cfg["keyless"]
    lines = [
        "# Pre-registration 2: Madrugada WINDOW 2 (summers 2018 to 2021)", "",
        f"Date: {today or date.today().isoformat()}. Written and committed BEFORE fetching or evaluating any window-2 "
        "data. Window-1 results (eval/results.json, summers 2022 to 2025) were already known when this was written; "
        "window 2 is an out-of-sample replication with the frozen code and rules.", "",
        "## Data", "",
        f"- Window: {j['season']['start']} to {j['season']['end']} of {', '.join(map(str, YEARS))}, plus the "
        f"{j['history_days_before_start']} days before each June 1 as history (evaluated only if they have their own "
        "7-day history, exactly as in window 1).",
        f"- Regions and sources (keyless, same as window 1): {', '.join(f'{r} (ASOS {v['icao']})' for r, v in k['regions'].items())}; "
        f"IEM ASOS temperature/RH and EPA AirData hourly PM2.5 (88101), nearest active monitor within {k['airdata']['max_km']} km.",
        f"- Separate cache: {CACHE_W2} (window 1's data/cache/ is never written). Fetched one year at a time with the "
        "frozen keyless job; a year whose AirData or IEM files are unavailable or incomplete is excluded and reported.",
        f"- Usability: >= {j['usable_fraction']:.0%} of slots observed for both temperature and PM2.5 after interpolating "
        f"gaps up to {j['max_gap_hours']} h. Forecast proxy, strata rule ({e['strata']}) and all other rules unchanged.", "",
        "## Analysis", "",
        "- Same functions as window 1 (eval/run_eval.run on the window-2 pool), called by analysis/eval_window2.py, which "
        "refuses to run unless these hashes match.",
        "- PRIMARY outcome: physical dominance (no more hours >=95F and no more AQI>=101 hours, strictly less on one). "
        "Comparisons: optimizer, robust (non-fallback days; and vs the optimizer on the same days) and oracle against "
        "B1, B2, b3_early, b3_late, by stratum and overall. Cost outcomes secondary.",
        f"- CIs: date-cluster bootstrap (seed {e['bootstrap']['seed']}, {e['bootstrap']['resamples']} resamples), none "
        f"for groups with fewer than {e['bootstrap']['min_n']} dates. Weight and forecast-proxy sensitivity as in window 1.",
        f"- Minimum {e['min_real_days']} real days. Window-2 results are reported separately and NEVER pooled with window "
        "1 in any confirmatory statement; a pooled table may appear only if labeled exploratory.",
        "- The start-time sensitivity repeated on window 2 is EXPLORATORY, POST-HOC (it was designed after window 1).", "",
        "## Hashes (SHA-256): must equal eval/PREREGISTRATION.md", "",
        "Same non-logic exclusions as eval/PREREGISTRATION.md; analysis/ files are non-logic.", "",
    ] + [f"- `{h}` {f}" for f, h in prereg.current_hashes().items()] + [""]
    return "\n".join(lines)


if __name__ == "__main__":
    problems = check_equal()
    if problems:
        sys.exit("STOP: hashes differ from eval/PREREGISTRATION.md: " + "; ".join(problems))
    if sys.argv[1:] == ["write"]:
        PREREG2.write_text(render(), encoding="utf-8")
        print(f"wrote {PREREG2}")
    ok, probs = prereg.verify(PREREG2)
    print("PREREGISTRATION_2 OK" if ok else "PREREGISTRATION_2 MISMATCH: " + "; ".join(probs))
