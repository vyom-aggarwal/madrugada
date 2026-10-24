"""Real-data inventory for the report: days used/excluded by region and year, exclusion reasons, sources and
monitor distances (from data/cache/meta/manifest.json), and the effective-sample-size note."""
import json
from collections import Counter
from pathlib import Path


def real_inventory(real_days: list[dict], manifest_path: Path) -> dict:
    used = Counter(f"{d['region']} {d['date'][:4]}" for d in real_days)
    m = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    reasons, by_ry = Counter(), Counter()
    for e in m.get("excluded", []):
        for r in e.get("reasons") or [e.get("reason", "?")]:
            reasons[r.split(":")[0] if ":" in r else r] += 1
        by_ry[f"{e['region']} {e.get('year') or e.get('date', '????')[:4]}"] += 1
    return {"path": m.get("path"), "years": m.get("years", {}), "sources": m.get("sources", {}),
            "used_by_region_year": dict(sorted(used.items())), "excluded_by_region_year": dict(sorted(by_ry.items())),
            "excluded_reasons": dict(reasons), "excluded": m.get("excluded", [])}


def ess_note(real_days: list[dict]) -> str:
    n = len(real_days)
    dates, regions = len({d["date"] for d in real_days}), len({d["region"] for d in real_days})
    return (f"{n} region-days on {dates} distinct dates in {regions} regions. Region-days on the same date (and "
            f"consecutive days) are correlated, so {n} is not the effective sample size; CIs resample whole dates.")
