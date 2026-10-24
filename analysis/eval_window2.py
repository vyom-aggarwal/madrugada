"""Evaluate WINDOW 2 with the frozen preregistered functions. Non-logic: imports and calls eval/run_eval.run on
the data/cache_w2/ pool without editing any hashed file; refuses unless eval/PREREGISTRATION_2.md hashes match.

Writes eval/results_w2.json, docs/results_w2.md (PREREGISTERED (WINDOW 2)) and, EXPLORATORY, POST-HOC,
analysis/start_sensitivity_w2.json (start-time sensitivity repeated on window 2).
Run: python -m analysis.eval_window2
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from analysis import describe, report_start, sensitivity_start  # noqa: E402
from analysis.prereg2 import PREREG2  # noqa: E402
from app.models import DayRecord  # noqa: E402
from eval import prereg, run_eval, stats  # noqa: E402
from eval.report import to_markdown  # noqa: E402

CACHE_W2 = ROOT / "data" / "cache_w2"
OUT_JSON, OUT_MD = ROOT / "eval" / "results_w2.json", ROOT / "docs" / "results_w2.md"
START_W2 = ROOT / "analysis" / "start_sensitivity_w2.json"
FIRST = ("PREREGISTERED (WINDOW 2): SUMMERS 2018 TO 2021, AIRPORT WEATHER AND NEARBY EPA MONITORS, MODELED "
         "EXPOSURE-HOURS ONLY")


def load_w2() -> dict:
    return {d.id: d for d in (DayRecord(**json.loads(p.read_text(encoding="utf-8")))
                              for p in sorted(CACHE_W2.glob("real-*.json")))}


def inventory_by_year(days: list[dict], records: dict) -> dict:
    hz = {d["id"]: describe.whole_day(records[d["id"]]) for d in days}
    inv = describe.strata_inventory(days, hz)
    per = defaultdict(lambda: {"days": 0, "days_aqi101": 0, "hours_aqi101": 0.0, "days_aqi151": 0, "hours_aqi151": 0.0})
    for d in days:
        y, h = per[d["date"][:4]], hz[d["id"]]
        y["days"] += 1
        y["days_aqi101"] += h["h101"] > 0
        y["hours_aqi101"] += h["h101"]
        y["days_aqi151"] += h["h151"] > 0
        y["hours_aqi151"] += h["h151"]
    inv["aqi_by_year"] = dict(sorted(per.items()))
    return inv


def main() -> int:
    ok, problems = prereg.verify(PREREG2)
    if not ok:
        print("REFUSED: eval/PREREGISTRATION_2.md missing or hashes differ: " + "; ".join(problems))
        return 4
    records = load_w2()
    run_eval.MANIFEST = CACHE_W2 / "meta" / "manifest.json"  # module attribute for this process only
    res = run_eval.run(pool=list(records.values()), prereg_path=PREREG2)
    days = [d for d in res["days"] if d["provenance"] == "real_cached"]
    res["window"] = "WINDOW 2: summers 2018 to 2021 (PREREGISTERED, eval/PREREGISTRATION_2.md)"
    res["window2_inventory"] = inventory_by_year(days, records)
    res["b3_smoke_wins"] = stats.b3_smoke_wins(days, run_eval.load_config())
    OUT_JSON.write_text(json.dumps(res, indent=1), encoding="utf-8")
    inv = res["window2_inventory"]
    extra = ["## Window-2 inventory by year (PREREGISTERED (WINDOW 2))", "",
             f"- Strata: {inv['by_stratum']}", f"- By year: {inv['by_year']}",
             f"- Days with any AQI>=101 hour: {inv['days_any_aqi101']} ({inv['total_hours_aqi101']:g} h); any AQI>=151: "
             f"{inv['days_any_aqi151']} ({inv['total_hours_aqi151']:g} h)", "",
             "| year | days | days AQI>=101 | hours AQI>=101 | days AQI>=151 | hours AQI>=151 |", "|---|---|---|---|---|---|"]
    extra += [f"| {y} | {v['days']} | {v['days_aqi101']} | {v['hours_aqi101']:g} | {v['days_aqi151']} | {v['hours_aqi151']:g} |"
              for y, v in inv["aqi_by_year"].items()]
    extra += ["", f"Optimizer has fewer AQI>=101 hours than b3_early on {res['b3_smoke_wins']['b3_early']} and than "
              f"b3_late on {res['b3_smoke_wins']['b3_late']} of {len(days)} days.", ""]
    md = [FIRST, "", *extra, to_markdown(res)]
    if len(days) >= 20:
        st = sensitivity_start.run([d["id"] for d in days], records, CACHE_W2 / "meta" / "manifest.json")
        START_W2.write_text(json.dumps(st, indent=1), encoding="utf-8")
        md += ["", "---", "", report_start.render(st, "Start-time sensitivity, WINDOW 2 (EXPLORATORY, POST-HOC: not "
                                                      "preregistered)")]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"{FIRST}\nwrote {OUT_JSON} and {OUT_MD}; real days {len(days)}; status {res['real_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
