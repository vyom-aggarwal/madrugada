"""Fetch WINDOW 2 (summers 2018 to 2021) with the frozen keyless job into data/cache_w2/. Non-logic.

Uses an in-memory copy of the config (years replaced); the global config and window 1's data/cache/ are never
touched. Runs one year at a time so an unavailable year is excluded and reported instead of stopping the job.
Refuses to run unless eval/PREREGISTRATION_2.md exists and its hashes match.
Run: python -m analysis.fetch_window2
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from analysis.prereg2 import PREREG2, YEARS  # noqa: E402
from app.config import load_config  # noqa: E402
from data import keyless_job, real_checks as rc  # noqa: E402
from data.fetcher import FetchError, Fetcher  # noqa: E402
from data.real_job import LIMITATIONS  # noqa: E402
from eval import prereg  # noqa: E402

CACHE_W2 = ROOT / "data" / "cache_w2"
NOTES_W2 = ROOT / "docs" / "real_data_notes_w2.md"


def main() -> int:
    ok, problems = prereg.verify(PREREG2)
    if not ok:
        print("REFUSED: eval/PREREGISTRATION_2.md missing or hashes differ: " + "; ".join(problems))
        return 4
    base = load_config()
    CACHE_W2.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(CACHE_W2 / "raw", base["real_job"]["throttle"])
    merged = {"path": "keyless (IEM ASOS + EPA AirData), window 2", "sources": {}, "excluded": [], "years": {}, "written": 0}
    checks, stops = [], []
    for y in YEARS:
        cfg = copy.deepcopy(base)
        cfg["real_job"]["years"] = [y]
        try:
            manifest, ch, stop = keyless_job.run(cfg, fetcher, CACHE_W2)
        except (FetchError, KeyError, ValueError, OSError) as e:  # e.g. IEM file unavailable for this year
            merged["years"][str(y)] = f"excluded: {e.__class__.__name__}: {e}"
            merged["excluded"].append({"region": "all", "year": y, "reason": f"year unavailable: {e}"})
            continue
        checks += ch
        if stop:
            stops.append(f"{y}: {stop}")
            merged["years"][str(y)] = f"excluded (stopped): {stop}"
            continue
        merged["years"][str(y)] = manifest["years"].get(str(y), "included")
        merged["excluded"] += manifest["excluded"]
        merged["written"] += manifest["written"]
        for region, src in manifest["sources"].items():
            merged["sources"].setdefault(region, {"asos": src["asos"], "monitors": {}})["monitors"].update(src["monitors"])
    n = len(list(CACHE_W2.glob("real-*.json")))
    summary = [f"window 2 days written this run: {merged['written']}", f"real_cached days in data/cache_w2: {n}",
               f"excluded entries: {len(merged['excluded'])}", f"years: {merged['years']}",
               f"network calls: {fetcher.network_calls}"] + [f"stopped: {s}" for s in stops]
    (CACHE_W2 / "meta").mkdir(parents=True, exist_ok=True)
    (CACHE_W2 / "meta" / "manifest.json").write_text(json.dumps({**merged, "summary": summary}, indent=1), encoding="utf-8")
    NOTES_W2.write_text(rc.notes_markdown(checks, merged["sources"], "; ".join(stops) or None, summary,
                                          LIMITATIONS["keyless"]).replace("# Real-data API notes", "# Real-data API notes: WINDOW 2"),
                        encoding="utf-8")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
