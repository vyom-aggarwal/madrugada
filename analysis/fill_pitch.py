"""Fill docs/PITCH.md placeholders from the result files -> docs/PITCH_filled.md. Verdict sentences are generated
from the numbers (CI excludes zero or not), never typed. Fails if a placeholder stays unfilled.
Sources: eval/results.json (window 1) and eval/results_w2.json (window 2), both preregistered; analysis/*.json
(EXPLORATORY, POST-HOC: not preregistered).

Run: python -m analysis.fill_pitch
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE, OUT = ROOT / "docs" / "PITCH.md", ROOT / "docs" / "PITCH_filled.md"


def _load(rel):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _ci(c, k, nd=2):
    return f"{c['ci95'][k][0]:+.{nd}f} to {c['ci95'][k][1]:+.{nd}f}" if c.get("ci95") else "no CI"


def _neg(c, k):  # CI entirely below zero
    return bool(c.get("ci95")) and c["ci95"][k][1] < 0


def _ov(res):
    return res["groups"]["real_cached"]["overall"]["comparisons"]


def _wtlm(p):
    return f"{p['win']}/{p['tie']}/{p['loss']}/{p['mixed']}"


def _start(st):
    s = {k: v["groups"]["overall"] for k, v in st["settings"].items()}
    a, b, c = (s[k]["optimizer_vs_B2"] for k in ("04:00", "05:30", "sunrise"))
    f = lambda x: f"{x['mean_diff']['hours_ge_95f']:+.3f} h/day (CI {_ci(x, 'hours_ge_95f', 3)})"  # noqa: E731
    gone = not _neg(b, "hours_ge_95f") and not _neg(c, "hours_ge_95f")
    verdict = (f"The benefit comes from the 04:00 earliest start, not from the planning: at a 05:30 earliest start it is "
               f"{f(b)}, and under a sunrise-minus-30-minutes rule {f(c)}. It rests on the assumption that a crew may "
               "start at 04:00, before dawn." if gone else
               f"Part of the benefit survives later starts: at 05:30 {f(b)}, sunrise rule {f(c)}.")
    return s, (a, b, c), f, verdict


def values() -> dict:
    r1, r2 = _load("eval/results.json"), _load("eval/results_w2.json")
    ex, st, demo = _load("analysis/exploratory_results.json"), _load("analysis/start_sensitivity.json"), _load("static/demo_snapshot.json")
    o1 = _ov(r1)["optimizer_vs_B2"]
    s, (a, b, c), f, verdict = _start(st)
    inv1 = ex["strata_inventory"]
    tod = ex["time_of_day"]["overall"]["cleanest_hours"]
    v = {"default_day": next((d["id"] for d in demo["days"] if "selected_by_rule" in d), demo["days"][0]["id"]),
         "w1_n": o1["n"], "w1_dates": o1["n_dates"], "w1_heat_cut": f"{-o1['mean_diff']['hours_ge_95f']:.2f}",
         "w1_heat_ci": _ci(o1, "hours_ge_95f"), "start_verdict": verdict,
         "start_short": f"at 05:30 {f(b)}; sunrise rule {f(c)}", "bsun_tie": s["04:00"]["optimizer_vs_B_sun"]["physical"]["tie"],
         "two_block_share": f"{st['settings']['04:00']['share_two_blocks']:.1%} at 04:00", "w1_phys_b2": _wtlm(o1["physical"]),
         "mixed_unchanged": ex["mixed_anatomy"]["overall"]["95F_and_AQI101_unchanged_other_metric_differs"],
         "mixed_total": ex["mixed_anatomy"]["overall"]["mixed_days"],
         "robust_fallback": len(r1["robust_fallback_days"]["real_cached"]),
         "smoke_why": (f"in window 1 only {inv1['days_any_aqi101']} of {o1['n']} region-days had any AQI>=101 hour, and the "
                       f"cleanest hours ({min(tod):02d}:00 to {max(tod):02d}:00) are the hottest.")}
    kms = [m["distance_km"] for res in (r1, r2) if res for s_ in res["real_inventory"]["sources"].values()
           for m in s_.get("monitors", {}).values()]
    v["monitor_km"] = f"{min(kms):.1f} to {max(kms):.1f}"
    w1_b3 = sum(d["plans"]["b3_late"]["hours_aqi_ge_101"] - d["plans"]["optimizer"]["hours_aqi_ge_101"] >= 0.125
                for d in r1["days"] if d["provenance"] == "real_cached")
    w12 = [f"window 1: fewer AQI>=101 hours than b3_late on {w1_b3} of {o1['n']} days"]
    if r2 and r2["n_days"]["real_cached"]:
        c2 = _ov(r2)
        o2, e2, l2 = c2["optimizer_vs_B2"], c2["optimizer_vs_b3_early"], c2["optimizer_vs_b3_late"]
        inv2 = r2["window2_inventory"]
        benefit = [x for x in (e2, l2) if _neg(x, "hours_aqi_ge_101")]
        v.update(w2_n=o2["n"], w2_dates=o2["n_dates"], w2_phys_b2=_wtlm(o2["physical"]),
                 w2_heat_cut_text=f"{o2['mean_diff']['hours_ge_95f']:+.2f} h/day (CI {_ci(o2, 'hours_ge_95f')})",
                 w2_heat_sentence=(f"Against B2 the plan changes hours at >=95F by {o2['mean_diff']['hours_ge_95f']:+.2f} "
                                   f"h/day (CI {_ci(o2, 'hours_ge_95f')}) and AQI>=101 hours by "
                                   f"{o2['mean_diff']['hours_aqi_ge_101']:+.3f} (CI {_ci(o2, 'hours_aqi_ge_101', 3)})."),
                 w2_smoke_sentence=(f"Versus heat-only planning it shows a smoke benefit: b3_early "
                                    f"{e2['mean_diff']['hours_aqi_ge_101']:+.3f} (CI {_ci(e2, 'hours_aqi_ge_101', 3)}), b3_late "
                                    f"{l2['mean_diff']['hours_aqi_ge_101']:+.3f} (CI {_ci(l2, 'hours_aqi_ge_101', 3)})."
                                    if benefit else
                                    f"For the optimizer, smoke avoidance did not change plans even in these years ({inv2['days_any_aqi101']} "
                                    f"region-days with any AQI>=101 hour, vs {inv1['days_any_aqi101']} in window 1): it ties "
                                    f"b3_early on {e2['physical']['tie']} of {e2['n']} days."))
        rb = c2["robust_vs_b3_early"]
        if _neg(rb, "hours_aqi_ge_101"):
            v["w2_smoke_sentence"] += (f" The scenario-averaged (robust) variant does show a small reduction vs heat-only "
                                       f"planning on its {rb['n']} non-fallback days: {rb['mean_diff']['hours_aqi_ge_101']:+.3f} "
                                       f"h/day at AQI>=101 (CI {_ci(rb, 'hours_aqi_ge_101', 3)}), at "
                                       f"{rb['mean_diff']['hours_ge_95f']:+.3f} h/day at >=95F (CI {_ci(rb, 'hours_ge_95f', 3)}).")
        w12.append(f"window 2: fewer than b3_late on {r2['b3_smoke_wins']['b3_late']} of {o2['n']} days")
    else:
        v.update(w2_n=0, w2_dates=0, w2_phys_b2="n/a", w2_heat_cut_text="not available",
                 w2_heat_sentence="Window 2 is not available.", w2_smoke_sentence="")
    v["w12_b3_smoke_text"] = "; ".join(w12)
    v["farms_answer"] = (f"That is where our benefit disappears. Against a fixed 05:30 start, the plan cuts hours at "
                         f">=95F only if crews may start earlier: with a 04:00 earliest start {f(a)}, at 05:30 {f(b)}, under "
                         f"a sunrise rule {f(c)}. A fixed shift starting at the earliest allowed time ties the optimizer on "
                         f"{v['bsun_tie']} of {o1['n']} days (EXPLORATORY, POST-HOC). So the honest pitch is a daily, "
                         "automatic heat-first schedule with smoke shown, not a smarter-than-early-start algorithm.")
    return v


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
