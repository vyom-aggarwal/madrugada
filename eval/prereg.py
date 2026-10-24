"""Pre-registration: freeze the evaluation rules and code before the first real eval.

`python -m eval.prereg write` writes eval/PREREGISTRATION.md (rules from config.yaml + SHA-256 hashes).
`verify()` recomputes the hashes; eval/run_eval.py refuses to evaluate real days if they differ.
Hashed: the logic files below and config.yaml without the documented non-logic keys (URLs, throttling).
Documented non-logic files (not hashed): presentation, API/UI, orchestration, tests, docs.
"""
import copy
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import CONFIG_PATH, load_config  # noqa: E402

PREREG_PATH = ROOT / "eval" / "PREREGISTRATION.md"
LOGIC_FILES = ["app/aqi.py", "app/baselines.py", "app/config.py", "app/exposure.py", "app/forecast.py",
               "app/models.py", "app/optimizer.py", "app/robust.py", "eval/metrics.py", "eval/prereg.py",
               "eval/run_eval.py", "eval/stats.py", "data/fetch_real.py", "data/keyless.py", "data/keyless_job.py",
               "data/real_checks.py"]
NON_LOGIC_FILES = ["eval/report.py", "eval/inventory.py", "eval/fixture_table.py", "app/main.py", "app/planning.py", "app/snapshot.py",
                   "app/crew_sheet.py", "static/*", "docs/*", "README.md", "tests/*", "tasks.py", "data/real_job.py",
                   "data/keyed.py", "data/fetcher.py", "CLAUDE.md"]
NON_LOGIC_CONFIG_KEYS = ["real_data.cimis.url", "real_data.airnow.url", "real_job.cimis_station_list_url",
                         "real_job.throttle", "keyless.iem.url", "keyless.airdata.url_template",
                         "keyless.airdata.listing_url"]
CONFIG_KEY = "config.yaml#logic"
LINE = re.compile(r"^- `([0-9a-f]{64})` (\S+)$")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def config_logic_hash(cfg: dict | None = None) -> str:
    c = copy.deepcopy(cfg or load_config())
    for path in NON_LOGIC_CONFIG_KEYS:
        *parents, leaf = path.split(".")
        node = c
        for p in parents:
            node = node.get(p, {})
        node.pop(leaf, None)
    return _sha(json.dumps(c, sort_keys=True).encode())


def current_hashes(root: Path = ROOT) -> dict[str, str]:
    """Line endings are normalized so a git checkout on another OS hashes the same."""
    out = {f: _sha((root / f).read_bytes().replace(b"\r\n", b"\n")) for f in LOGIC_FILES}
    out[CONFIG_KEY] = config_logic_hash()
    return out


def verify(path: Path = PREREG_PATH) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"{path.name} not found"]
    recorded = {m.group(2): m.group(1) for m in map(LINE.match, path.read_text(encoding="utf-8").splitlines()) if m}
    now = current_hashes()
    problems = [f"{k}: {'missing from file' if k not in recorded else 'hash differs'}"
                for k in now if recorded.get(k) != now[k]]
    return not problems, problems


def render(today: str | None = None) -> str:
    cfg = load_config()
    j, e, k = cfg["real_job"], cfg["eval"], cfg["keyless"]
    lines = [
        "# Pre-registration: Madrugada real-data evaluation", "",
        f"Date: {today or date.today().isoformat()}. Written and committed BEFORE the first real-data eval.", "",
        "## Data", "",
        f"- Regions: {', '.join(f'{r} ({v['label']}, ASOS {v['icao']})' for r, v in k['regions'].items())}.",
        f"- Window: {j['season']['start']} to {j['season']['end']} of {', '.join(map(str, j['years']))}; plus the "
        f"{j['history_days_before_start']} days before each season start as forecast history only (evaluated if they "
        "have their own 7-day history, like every other day).",
        "- Sources: CIMIS + AirNow if both keys are set, otherwise IEM ASOS (temperature, RH) + EPA AirData hourly "
        f"PM2.5 (88101; nearest active monitor within {k['airdata']['max_km']} km of the ASOS station).",
        f"- Usable day: >= {j['usable_fraction']:.0%} of 15-minute slots observed for BOTH temperature and PM2.5 after "
        f"linear interpolation of gaps up to {j['max_gap_hours']} h. Years whose AirData file is missing or incomplete "
        "are excluded. All usable days are evaluated; none are selected after seeing results.", "",
        "## Rules", "",
        f"- Strata on observed data: heat = max temp >= {e['strata']['heat_temp_f']}F, smoke = max AQI >= "
        f"{e['strata']['smoke_aqi']}; heat_only, smoke_only, co_occurring (both), mild (neither).",
        "- PRIMARY outcome: physical dominance (win = no more hours >=95F and no more AQI>=101 hours, strictly less on "
        f"one; loss = reverse; tie = all physical metrics within {e['tie_hours']} h; else mixed). Cost-based outcomes are "
        "secondary (\"uses the optimizer's own cost\").",
        "- Comparisons: optimizer, robust, oracle (upper bound) against B1, B2, b3_early, b3_late, by stratum and overall. "
        "Robust only on days without fallback, and against the optimizer on those same days.",
        f"- CIs: cluster bootstrap over calendar dates (seed {e['bootstrap']['seed']}, {e['bootstrap']['resamples']} "
        f"resamples), skipped for groups with fewer than {e['bootstrap']['min_n']} dates. Region-days are not the "
        "effective sample size.",
        f"- Weight sensitivity: w_heat {e['sensitivity']['w_heat']}, w_smoke {e['sensitivity']['w_smoke']}, w_dual "
        f"{e['sensitivity']['w_dual']}, cost levels {e['sensitivity']['cost_levels']}; headline day-level.",
        f"- Forecast-proxy sensitivity: {list(e['forecast_proxies'])} and the default blend.",
        "- Secondary: NowCast-based hours at AQI>=101 and >=151 (observed only; planning unchanged).",
        f"- Minimum real days for any real-data conclusion: {e['min_real_days']}. Real and synthetic days never pooled.", "",
        "## Hashes (SHA-256)", "",
        "Config hash excludes the non-logic keys: " + ", ".join(NON_LOGIC_CONFIG_KEYS) + ".",
        "Documented non-logic files (not hashed): " + ", ".join(NON_LOGIC_FILES) + ".", "",
    ] + [f"- `{h}` {f}" for f, h in current_hashes().items()] + [""]
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1:] == ["write"]:
        PREREG_PATH.write_text(render(), encoding="utf-8")
        print(f"wrote {PREREG_PATH}")
    else:
        ok, problems = verify()
        print("preregistration OK" if ok else "preregistration MISMATCH: " + "; ".join(problems))
