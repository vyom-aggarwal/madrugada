"""Real-data job (python tasks.py real).

Source priority: CIMIS + AirNow when CIMIS_APPKEY and AIRNOW_KEY are both set (data/keyed.py), otherwise
the keyless IEM ASOS + EPA AirData path (data/keyless_job.py). Raw responses are cached under
data/cache/raw/ (resume without re-downloading); DayRecords go to data/cache/<id>.json
(provenance="real_cached"); sources and exclusions go to data/cache/meta/manifest.json; live API checks go
to docs/real_data_notes.md. The real eval runs only if eval/PREREGISTRATION.md exists and its hashes match,
and only with at least `eval.min_real_days` real days.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import load_config  # noqa: E402
from data import real_checks as rc  # noqa: E402
from data.fetcher import FetchError, Fetcher  # noqa: E402,F401  (re-exported for callers/tests)
from data.real_checks import pending, season_days  # noqa: E402,F401

CACHE = ROOT / "data" / "cache"
NOTES = ROOT / "docs" / "real_data_notes.md"
KEYS = ("CIMIS_APPKEY", "AIRNOW_KEY")
LIMITATIONS = {
    "keyless": ["Airport (ASOS) air temperature is not field temperature; fields can be hotter, and sun load is not "
                "measured (solar_wm2 is unavailable and set to 0).",
                "The PM2.5 monitor may be miles from the field; the distance is recorded per day.",
                "ASOS reports are interpolated to 15-minute slots; AirData hourly values fill their four slots."],
    "cimis_airnow": ["CIMIS stations sit over irrigated grass; field temperature can differ.",
                     "The AirNow monitor may be miles from the field; the distance is recorded per day."],
}


def choose_path(env) -> str:
    """'cimis_airnow' if both keys are set, otherwise 'keyless'."""
    return "cimis_airnow" if all(env.get(k) for k in KEYS) else "keyless"


def main() -> int:
    cfg = load_config()
    path = choose_path(os.environ)
    print(f"real_job: source path = {path}")
    fetcher = Fetcher(CACHE / "raw", cfg["real_job"]["throttle"])
    if path == "cimis_airnow":
        from data import keyed
        manifest, checks, stop = keyed.run(cfg, fetcher, CACHE, {k: os.environ[k] for k in KEYS})
    else:
        from data import keyless_job
        manifest, checks, stop = keyless_job.run(cfg, fetcher, CACHE)
    n_real = len(list(CACHE.glob("real-*.json")))
    reasons: dict[str, int] = {}
    for e in manifest["excluded"]:
        for r in e.get("reasons", [e.get("reason", "?")]):
            key = r.split(":")[0] if ":" in r else r
            reasons[key] = reasons.get(key, 0) + 1
    summary = [f"source path: {manifest.get('path', path)}", f"days written this run: {manifest.get('written', 0)}",
               f"real_cached days in cache: {n_real}", f"excluded entries this run: {len(manifest['excluded'])} {reasons}",
               f"years: {manifest.get('years', {})}", f"network calls: {fetcher.network_calls}"]
    (CACHE / "meta").mkdir(parents=True, exist_ok=True)
    (CACHE / "meta" / "manifest.json").write_text(json.dumps({**manifest, "summary": summary}, indent=1), encoding="utf-8")
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text(rc.notes_markdown(checks, manifest["sources"], stop, summary, LIMITATIONS[path]), encoding="utf-8")
    print("\n".join(summary))
    if stop:
        print(f"real_job STOPPED: {stop} See {NOTES}.")
        return 3
    if n_real < cfg["eval"]["min_real_days"]:
        print(f"insufficient real days ({n_real} < {cfg['eval']['min_real_days']}); real eval not run.")
        return 0
    from eval.prereg import verify
    ok, problems = verify()
    if not ok:
        print("real eval not run: eval/PREREGISTRATION.md missing or hashes differ: " + "; ".join(problems))
        return 0
    from app.snapshot import main as build_snapshot
    from eval.run_eval import main as run_eval
    run_eval()
    build_snapshot()
    return 0


if __name__ == "__main__":
    sys.exit(main())
