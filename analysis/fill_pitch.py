"""Fill docs/PITCH.md placeholders -> docs/PITCH_filled.md. Every number comes from eval/results.json (window 1),
eval/results_w2.json (window 2) or analysis/start_sensitivity*.json (EXPLORATORY, POST-HOC). Verdicts are generated
from the CIs, never typed. Each window keeps its own CI; nothing is pooled. Fails on an unfilled placeholder.

Run: python -m analysis.fill_pitch
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE, OUT = ROOT / "docs" / "PITCH.md", ROOT / "docs" / "PITCH_filled.md"
HEAT, SMOKE = "hours_ge_95f", "hours_aqi_ge_101"
FMT = {HEAT: 2, SMOKE: 3}


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def fmt(c: dict, k: str, d: int | None = None) -> str:
    """'mean h/day (CI lo to hi)', with the decimals used everywhere (audited against the JSON)."""
    d = FMT[k] if d is None else d
    m = f"{c['mean_diff'][k]:+.{d}f} h/day"
    return m + (f" (CI {c['ci95'][k][0]:+.{d}f} to {c['ci95'][k][1]:+.{d}f})" if c.get("ci95") else " (no CI)")


def below(c: dict, k: str) -> bool:
    return bool(c.get("ci95")) and c["ci95"][k][1] < 0


def overall(res: dict) -> dict:
    return res["groups"]["real_cached"]["overall"]["comparisons"]


def start(st: dict, k: str) -> dict:
    return st["settings"][k]["groups"]["overall"]["optimizer_vs_B2"]


def sources() -> dict:
    """Headline comparisons by name, read from the result files (also used by the claims audit)."""
    r1, r2 = load("eval/results.json"), load("eval/results_w2.json")
    s1, s2 = load("analysis/start_sensitivity.json"), load("analysis/start_sensitivity_w2.json")
    c1, c2 = overall(r1), overall(r2)
    return {"r1": r1, "r2": r2, "s1": s1, "s2": s2,
            "w1_heat": (c1["optimizer_vs_B2"], HEAT), "w2_heat": (c2["optimizer_vs_B2"], HEAT),
            "w1_0530": (start(s1, "05:30"), HEAT, 3), "w1_sun": (start(s1, "sunrise"), HEAT, 3),
            "w2_0530": (start(s2, "05:30"), HEAT, 3), "w2_sun": (start(s2, "sunrise"), HEAT, 3),
            "w2_smoke_b2": (c2["optimizer_vs_B2"], SMOKE),
            "w1_b3_smoke": (c1["optimizer_vs_b3_early"], SMOKE), "w2_b3_smoke": (c2["optimizer_vs_b3_early"], SMOKE)}


def values() -> dict:
    src = sources()
    r1, r2, s1 = src["r1"], src["r2"], src["s1"]
    c1, c2 = overall(r1), overall(r2)
    v = {k: fmt(*src[k]) for k in src if k.startswith("w")}
    only04 = (below(*src["w1_heat"][:2]) and not any(below(*src[k][:2]) for k in ("w1_0530", "w1_sun", "w2_0530", "w2_sun")))
    v["heat_verdict"] = ("Shifting hours reduces heat exposure only if crews can start before dawn (04:00)" if only04 else
                         "The heat result depends on the earliest start allowed")
    w2b2 = ("a small reduction vs the early fixed shift in window 2, " + v["w2_smoke_b2"] if below(*src["w2_smoke_b2"])
            else "no clear change vs the early fixed shift in window 2, " + v["w2_smoke_b2"])
    b3 = ("some reduction vs heat-only planning" if below(*src["w1_b3_smoke"]) or below(*src["w2_b3_smoke"])
          else "none vs heat-only planning")
    v["smoke_verdict"] = (f"{w2b2}; {b3} (AQI>=101 vs b3_early: window 1 {v['w1_b3_smoke']}, window 2 "
                          f"{v['w2_b3_smoke']}).")
    o1, o2 = c1["optimizer_vs_B2"], c2["optimizer_vs_B2"]
    p = o1["physical"]
    v.update(w1_n=o1["n"], w2_n=o2["n"], w1_dates=o1["n_dates"], w2_dates=o2["n_dates"],
             w1_b3_tie=c1["optimizer_vs_b3_early"]["physical"]["tie"], w2_b3_tie=c2["optimizer_vs_b3_early"]["physical"]["tie"],
             w1_phys=f"{p['win']}/{p['tie']}/{p['loss']}/{p['mixed']}",
             bsun_tie=s1["settings"]["04:00"]["groups"]["overall"]["optimizer_vs_B_sun"]["physical"]["tie"],
             two_block=f"{s1['settings']['04:00']['share_two_blocks']:.1%}")
    mons = [(m["distance_km"], region, y) for res in (r1, r2) for region, s in res["real_inventory"]["sources"].items()
            for y, m in s.get("monitors", {}).items()]
    far = max(mons)
    far_years = sorted(y for d, r, y in mons if r == far[1] and d == far[0])
    v["max_km"] = f"{far[0]:.2f}"
    v["tulare_note"] = (f"PM2.5 monitors are {min(mons)[0]:.2f} to {far[0]:.2f} km from the weather stations; the "
                        f"farthest is {far[1].capitalize()} in {far_years[0]}-{far_years[-1]} (window 2)")
    excl = sorted({(e["region"], e["year"]) for e in r2["real_inventory"]["excluded"]
                   if "monitor" in str(e.get("reason", ""))})
    regions = sorted({r for r, _ in excl})
    v["excluded_note"] = ("; ".join(f"{r.capitalize()} {min(y for rr, y in excl if rr == r)}-"
                                    f"{max(y for rr, y in excl if rr == r)} excluded in window 2 (no active PM2.5 monitor "
                                    "within 25 km)" for r in regions) if excl else "No region-years excluded for monitor distance")
    return v


def main() -> None:
    v = values()
    text = re.sub(r"\{\{(\w+)\}\}", lambda m: str(v[m.group(1)]), TEMPLATE.read_text(encoding="utf-8"))
    text = text.replace("# Madrugada pitch (template)", "# Madrugada pitch (filled from the result files; start-time "
                        "numbers are EXPLORATORY, POST-HOC: not preregistered)")
    left = re.findall(r"\{\{\w+\}\}", text)
    if left:
        sys.exit(f"unfilled placeholders: {left}")
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
