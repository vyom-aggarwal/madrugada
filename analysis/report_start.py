"""EXPLORATORY, POST-HOC: not preregistered. Renders a start-sensitivity JSON (analysis.sensitivity_start) to
markdown, with plain statements generated from the numbers. Non-logic.

Run: python -m analysis.report_start   (window 1 -> docs/start_sensitivity.md)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FIRST = "EXPLORATORY, POST-HOC: NOT PREREGISTERED"


def ci(c: dict, k: str = "hours_ge_95f") -> str:
    m = c["mean_diff"][k]
    if m is None:
        return "-"
    return f"{m:+.3f}" + (f" [{c['ci95'][k][0]:+.3f}, {c['ci95'][k][1]:+.3f}]" if c["ci95"] else " (n<10 dates: no CI)")


def excludes_zero(c: dict, k: str = "hours_ge_95f") -> bool:
    return bool(c["ci95"]) and (c["ci95"][k][1] < 0 or c["ci95"][k][0] > 0)


def wtlm(p: dict) -> str:
    return f"{p['win']}/{p['tie']}/{p['loss']}/{p['mixed']}"


def statements(r: dict) -> list[str]:
    s = r["settings"]
    g = {k: v["groups"]["overall"] for k, v in s.items()}
    base = g["04:00"]["optimizer_vs_B2"]["mean_diff"]["hours_ge_95f"]
    out = []
    for k in ("05:30", "sunrise"):
        c = g[k]["optimizer_vs_B2"]
        m = c["mean_diff"]["hours_ge_95f"]
        share = (m / base) if base else float("nan")
        verdict = ("clearly fewer hours" if excludes_zero(c) and m < 0 else
                   "clearly MORE hours" if excludes_zero(c) and m > 0 else "no clear difference")
        remains = (f"{share:.0%} of the 04:00 benefit ({base:+.3f} h/day) remains" if m < 0 else
                   f"none of the 04:00 benefit ({base:+.3f} h/day) remains")
        out.append(f"At earliest start {k}, the optimizer vs B2 has {ci(c)} h/day at >=95F, about {m * 60:+.1f} "
                   f"min/day ({verdict}); {remains}.")
    for k in ("04:00", "05:30", "sunrise"):
        one, split = g[k]["optimizer_1block_vs_B2"], g[k]["optimizer_vs_optimizer_1block"]
        out.append(f"{k}: one block placed by the optimizer vs B2 {ci(one)}; adding a second block (two-block vs "
                   f"one-block) {ci(split)}. Two-block plans chosen on {s[k]['share_two_blocks']:.1%} of days.")
    sun = g["04:00"]["optimizer_vs_B_sun"]
    out.append(f"Against B_sun (a fixed shift at the same earliest start) the optimizer has {ci(sun)} at 04:00, "
               f"physical W/T/L/M {wtlm(sun['physical'])}: the heat benefit vs B2 comes from starting at the earliest "
               "allowed time, not from splitting the shift or from the forecast.")
    return out


def render(r: dict, title: str = "Start-time sensitivity (window 1, summers 2022 to 2025)") -> str:
    lines = [FIRST, "", f"# {title}", "",
             f"{r['n_days']} real region-days on {r['n_dates']} dates. Paid hours 8.5, latest end, min block and min gap "
             "as in config. B_sun = a fixed 8.5 h shift starting at the setting's earliest start. The sunrise rule uses "
             "approximate, unverified NOAA equations (sunrise minus 30 min, rounded to 15 min); station coordinates: "
             f"{r['coords']}. CIs are date-cluster bootstrap (frozen seed, 10,000 resamples).", "",
             "## What this shows", ""] + [f"- {x}" for x in statements(r)] + ["",
             "## Hours >=95F, mean difference per day [95% CI], overall", "",
             "| earliest | opt vs B2 | opt vs B_sun | oracle vs B2 | oracle vs B_sun | 1-block vs B2 | 2-block vs 1-block "
             "| two-block share | median gap h | mean h95 B2 / B_sun / opt |", "|---" * 10 + "|"]
    for k, v in r["settings"].items():
        g = v["groups"]["overall"]
        mh = v["mean_h95"]
        lines.append(f"| {k} | {ci(g['optimizer_vs_B2'])} | {ci(g['optimizer_vs_B_sun'])} | {ci(g['oracle_vs_B2'])} | "
                     f"{ci(g['oracle_vs_B_sun'])} | {ci(g['optimizer_1block_vs_B2'])} | "
                     f"{ci(g['optimizer_vs_optimizer_1block'])} | {v['share_two_blocks']:.1%} | {v['median_gap_h']} | "
                     f"{mh['B2']} / {mh['B_sun']} / {mh['optimizer']} |")
    lines += ["", "## Physical dominance W/T/L/mixed and other metrics, overall", "",
              "| earliest | opt vs B2 | opt vs B_sun | oracle vs B2 | h>=80F opt vs B2 | AQI>=101 opt vs B2 |", "|---" * 6 + "|"]
    for k, v in r["settings"].items():
        g = v["groups"]["overall"]
        lines.append(f"| {k} | {wtlm(g['optimizer_vs_B2']['physical'])} | {wtlm(g['optimizer_vs_B_sun']['physical'])} | "
                     f"{wtlm(g['oracle_vs_B2']['physical'])} | {ci(g['optimizer_vs_B2'], 'hours_ge_80f')} | "
                     f"{ci(g['optimizer_vs_B2'], 'hours_aqi_ge_101')} |")
    lines += ["", "## By stratum: optimizer vs B2, hours >=95F [95% CI]", "",
              "| earliest | " + " | ".join(r["settings"]["04:00"]["groups"]) + " |", "|---" * 6 + "|"]
    for k, v in r["settings"].items():
        lines.append(f"| {k} | " + " | ".join(f"{ci(c['optimizer_vs_B2'])} (n={c['optimizer_vs_B2']['n']})"
                                              for c in v["groups"].values()) + " |")
    lines += ["", "## Chosen start times (optimizer, first block)", ""]
    lines += [f"- {k}: {v['start_times']}" + (f" (sunrise-rule earliest starts: {v['earliest_values']})" if k == "sunrise" else "")
              for k, v in r["settings"].items()]
    return "\n".join(lines + [""])


def main(src: Path = ROOT / "analysis" / "start_sensitivity.json", out: Path = ROOT / "docs" / "start_sensitivity.md") -> None:
    out.write_text(render(json.loads(src.read_text(encoding="utf-8"))), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
