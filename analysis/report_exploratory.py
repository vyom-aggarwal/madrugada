"""EXPLORATORY, POST-HOC: not preregistered. Renders analysis/exploratory_results.json (from analysis.describe)
into docs/exploratory_findings.md, including a 'What this does and does not support' section generated
from the numbers. Non-logic; edits no hashed file.

Run: python -m analysis.report_exploratory
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from eval.metrics import STRATA  # noqa: E402

SRC = ROOT / "analysis" / "exploratory_results.json"
OUT = ROOT / "docs" / "exploratory_findings.md"
FIRST = ("EXPLORATORY, POST-HOC: NOT PREREGISTERED. SUMMER 2022 TO 2025, AIRPORT WEATHER AND NEARBY EPA MONITORS, "
         "MODELED EXPOSURE-HOURS ONLY.")
TAG = "_EXPLORATORY, POST-HOC: not preregistered._"


def _ci(x):
    if x["mean"] is None:
        return "-"
    return f"{x['mean']:+.3f}" + (f" [{x['ci95'][0]:+.3f}, {x['ci95'][1]:+.3f}]" if x["ci95"] else " (n too small for CI)")


def _table(head, rows):
    return ["| " + " | ".join(map(str, head)) + " |", "|---" * len(head) + "|"] + [
        "| " + " | ".join(str(c) for c in r) + " |" for r in rows] + [""]


def support(r: dict) -> list[str]:
    inv, eff, mx, sm, tod = (r[k] for k in ("strata_inventory", "effect_by_stratum", "mixed_anatomy",
                                            "smoke_movability", "time_of_day"))
    o = eff["optimizer_vs_B2|overall"]
    ov = mx["overall"]
    trade = ov["heat_down_smoke_up"] + ov["heat_up_smoke_down"]
    t = tod["overall"]
    supports = [
        f"Heat: vs B2 the optimizer has {o['hours_ge_95f']['mean']:+.2f} h/day at >=95F (CI {o['hours_ge_95f']['ci95']}) "
        f"and {o['hours_ge_80f']['mean']:+.2f} h/day at >=80F (CI {o['hours_ge_80f']['ci95']}).",
        f"Mixed days vs B2 are mostly not heat-for-smoke trade-offs: {ov['95F_and_AQI101_unchanged_other_metric_differs']} of "
        f"{ov['mixed_days']} have identical >=95F and AQI>=101 hours and differ in another metric (median change in "
        f">=80F hours {ov.get('unchanged_case_change_h80', {}).get('median')}); {trade} are trade-offs.",
    ]
    does_not = [
        f"A smoke benefit: AQI>=101 difference vs B2 is {o['hours_aqi_ge_101']['mean']:+.4f} h/day "
        f"(CI {o['hours_aqi_ge_101']['ci95']}).",
        f"Smoke was rare: {inv['days_any_aqi101']} of {r['n_days']} region-days had any AQI>=101 hour "
        f"({inv['total_hours_aqi101']:g} h in total) and {inv['days_any_aqi151']} had any AQI>=151 hour "
        f"({inv['total_hours_aqi151']:g} h). Smoke-only and co-occurring strata have "
        f"{inv['by_stratum']['smoke_only']['dates']} and {inv['by_stratum']['co_occurring']['dates']} dates.",
        f"Smoke is hard to move even with perfect knowledge: on the {sm['smoke_days']} days with >=1 AQI>=101 hour the "
        f"oracle removes {sm['oracle_removed_h101_vs_B2']['total']:g} smoke hours vs B2 in total (mean "
        f"{sm['oracle_removed_h101_vs_B2']['mean']} h/day, median {sm['oracle_removed_h101_vs_B2']['median']}).",
        f"Time of day: mean AQI is lowest at hours {t['cleanest_hours']} and highest at {t['dirtiest_hours']}; temperature "
        f"is lowest at {t['coolest_hours']} and highest at {t['hottest_hours']}. The cleanest hours "
        f"{'coincide' if set(t['cleanest_hours']) & set(t['coolest_hours']) else 'do not coincide'} with the coolest hours.",
        "Any field-level, health or compliance claim: airport temperature and monitors several km away; modeled "
        "exposure-hours only.",
    ]
    return ["## What this does and does not support", "", "Supports:", ""] + [f"- {s}" for s in supports] + [
        "", "Does not support:", ""] + [f"- {s}" for s in does_not] + [""]


def render(r: dict) -> str:
    inv = r["strata_inventory"]
    lines = [FIRST, "", "# Exploratory findings (real data)", "", TAG, "",
             f"{r['n_days']} real region-days on {r['n_dates']} dates (the preregistered evaluation set). Strata use the "
             "frozen rule. Differences are optimizer minus baseline; CIs are date-cluster bootstrap (frozen seed, "
             "10,000 resamples), skipped for groups with fewer than 10 dates.", "",
             "## 1. Strata inventory", "", TAG, ""]
    lines += _table(["stratum", "region-days", "dates"], [[s, v["days"], v["dates"]] for s, v in inv["by_stratum"].items()])
    for key in ("by_region", "by_year"):
        lines += _table([key.replace("by_", ""), *STRATA], [[k, *(v.get(s, 0) for s in STRATA)] for k, v in inv[key].items()])
    lines += [f"Days with any observed AQI>=101 hour: {inv['days_any_aqi101']} ({inv['total_hours_aqi101']:g} h total); "
              f"any AQI>=151 hour: {inv['days_any_aqi151']} ({inv['total_hours_aqi151']:g} h total).", "",
              "## 2. Effect by stratum (mean difference [95% CI])", "", TAG, ""]
    rows = []
    for k, v in r["effect_by_stratum"].items():
        comp, g = k.split("|")
        rows.append([comp.replace("_vs_", " vs "), g, v["n"], v["dates"], _ci(v["hours_ge_95f"]), _ci(v["hours_ge_80f"]),
                     _ci(v["hours_aqi_ge_101"])])
    lines += _table(["comparison", "stratum", "n", "dates", "h >=95F", "h >=80F", "h AQI>=101"], rows)
    lines += ["## 3. Anatomy of 'mixed' days vs B2", "", TAG, ""]
    lines += _table(["stratum", "mixed", "heat down, smoke up", "heat up, smoke down", "95F & AQI101 unchanged",
                     "heat-down side: -h95 median/p90", "smoke-up side: +h101 median/p90", "unchanged: h80 change median"],
                    [[g, v["mixed_days"], v["heat_down_smoke_up"], v["heat_up_smoke_down"],
                      v["95F_and_AQI101_unchanged_other_metric_differs"],
                      f"{v['heat_down_smoke_up_change_h95']['median']}/{v['heat_down_smoke_up_change_h95']['p90']}",
                      f"{v['heat_down_smoke_up_change_h101']['median']}/{v['heat_down_smoke_up_change_h101']['p90']}",
                      v.get("unchanged_case_change_h80", {}).get("median")] for g, v in r["mixed_anatomy"].items()])
    sm = r["smoke_movability"]
    lines += ["## 4. Smoke movability (days with >= 1 observed AQI>=101 hour)", "", TAG, "",
              f"- Smoke days: {sm['smoke_days']}.",
              f"- Oracle vs B2, AQI>=101 hours removed: total {sm['oracle_removed_h101_vs_B2']['total']:g}, mean "
              f"{sm['oracle_removed_h101_vs_B2']['mean']}, median {sm['oracle_removed_h101_vs_B2']['median']}; days with any "
              f"removed: {sm['oracle_removed_h101_vs_B2']['days_any_removed']}.",
              f"- Oracle vs B2, change in hours >=95F on the same days: total {sm['oracle_added_h95_vs_B2']['total']:g}, "
              f"mean {sm['oracle_added_h95_vs_B2']['mean']} (negative = fewer heat hours).",
              f"- AQI>=101 hours inside the heat-optimal window (heat-only optimizer on observed data): "
              f"{sm['smoke_hours_inside_heat_optimal_window']:g} h; outside it but within the allowed 04:00-19:00 window: "
              f"{sm['smoke_hours_outside_window_in_allowed_hours']:g} h; outside the allowed window: "
              f"{sm['smoke_hours_outside_allowed_hours']:g} h.",
              f"- Smoke days by where their in-window smoke hours fall: {sm['days_by_location_within_allowed_hours']}.", "",
              "## 5. Time of day: mean observed AQI and temperature by local clock hour", "", TAG, ""]
    for g, v in r["time_of_day"].items():
        lines += [f"**{g}** (n={v['n']}): cleanest hours {v['cleanest_hours']}, dirtiest {v['dirtiest_hours']}, coolest "
                  f"{v['coolest_hours']}, hottest {v['hottest_hours']}.", ""]
        lines += _table(["hour", *range(24)], [["AQI", *v["mean_aqi_by_hour"]], ["temp F", *v["mean_temp_by_hour"]]])
    return "\n".join(lines + support(r))


def main() -> None:
    OUT.write_text(render(json.loads(SRC.read_text(encoding="utf-8"))), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
