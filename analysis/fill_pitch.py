"""Fill docs/PITCH.md placeholders from eval/results.json (preregistered) and analysis/exploratory_results.json
(EXPLORATORY, POST-HOC: not preregistered) -> docs/PITCH_filled.md. Fails if any placeholder stays unfilled.

Run: python -m analysis.fill_pitch
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE, OUT = ROOT / "docs" / "PITCH.md", ROOT / "docs" / "PITCH_filled.md"


def _ci(c, k, nd=2):
    return f"{c['ci95'][k][0]:+.{nd}f} to {c['ci95'][k][1]:+.{nd}f}" if c.get("ci95") else "n/a"


def values() -> dict:
    res = json.loads((ROOT / "eval" / "results.json").read_text(encoding="utf-8"))
    ex = json.loads((ROOT / "analysis" / "exploratory_results.json").read_text(encoding="utf-8"))
    demo = json.loads((ROOT / "static" / "demo_snapshot.json").read_text(encoding="utf-8"))
    c = res["groups"]["real_cached"]["overall"]["comparisons"]
    o, e, orc = c["optimizer_vs_B2"], c["optimizer_vs_b3_early"], c["oracle_vs_B2"]
    p = o["physical"]
    tod = ex["time_of_day"]["overall"]
    mx = ex["mixed_anatomy"]["overall"]
    h80 = ex["effect_by_stratum"]["optimizer_vs_B2|overall"]["hours_ge_80f"]
    kms = [m["distance_km"] for s in res["real_inventory"]["sources"].values() for m in s.get("monitors", {}).values()]
    b3l = sum(d["plans"]["b3_late"]["hours_aqi_ge_101"] - d["plans"]["optimizer"]["hours_aqi_ge_101"] >= 0.125
              for d in res["days"] if d["provenance"] == "real_cached")
    return {
        "default_day": next((d["id"] for d in demo["days"] if "selected_by_rule" in d), demo["days"][0]["id"]),
        "real_n": o["n"], "real_dates": o["n_dates"],
        "heat95_cut": f"{-o['mean_diff']['hours_ge_95f']:.2f}", "heat95_ci": _ci(o, "hours_ge_95f"),
        "smoke_mean": f"{o['mean_diff']['hours_aqi_ge_101']:+.3f}", "smoke_ci": _ci(o, "hours_aqi_ge_101", 3),
        "b3e_tie": e["physical"]["tie"], "oracle_smoke": f"{orc['mean_diff']['hours_aqi_ge_101']:+.3f}",
        "days_aqi101": ex["strata_inventory"]["days_any_aqi101"],
        "cleanest": "-".join(f"{h:02d}:00" for h in sorted(tod["cleanest_hours"])[::2]),
        "coolest": "-".join(f"{h:02d}:00" for h in sorted(tod["coolest_hours"])[::2]),
        "heat80_cut": f"{-h80['mean']:.2f}", "b3_smoke_wins": b3l,
        "phys_b2": f"{p['win']}/{p['tie']}/{p['loss']}/{p['mixed']}",
        "weak_day": f"{res['weight_sensitivity']['real_cached']['overall']['day_level_weakly_dominates']:.1%}",
        "strict_day": f"{res['weight_sensitivity']['real_cached']['overall']['day_level_strictly_improves']:.1%}",
        "monitor_km": f"{min(kms):.1f} to {max(kms):.1f}",
        "mixed_unchanged": mx["95F_and_AQI101_unchanged_other_metric_differs"], "mixed_total": mx["mixed_days"],
        "robust_fallback": len(res["robust_fallback_days"]["real_cached"]),
    }


def main() -> None:
    v = values()
    text = re.sub(r"\{\{(\w+)\}\}", lambda m: str(v[m.group(1)]), TEMPLATE.read_text(encoding="utf-8"))
    text = text.replace("# Madrugada pitch (template)", "# Madrugada pitch (filled from results; exploratory numbers "
                        "are labeled EXPLORATORY, POST-HOC: not preregistered)")
    left = re.findall(r"\{\{\w+\}\}", text)
    if left:
        sys.exit(f"unfilled placeholders: {left}")
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
