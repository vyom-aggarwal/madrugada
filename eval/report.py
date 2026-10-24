"""Markdown rendering of eval results (eval/results.md). First line is the provenance statement."""
from eval.metrics import BASELINES, CHALLENGERS, PHYS, PLANS


def _wtl(r: dict) -> str:
    return f"{r['win']}/{r['tie']}/{r['loss']}/{r['mixed']}"


def _diff(r: dict, k: str) -> str:
    if not r["mean_diff"]:
        return "-"
    ci = r["ci95"][k] if r["ci95"] else None
    return f"{r['mean_diff'][k]:+g}" + (f" [{ci[0]:+g}, {ci[1]:+g}]" if ci else "")


def _group(lines: list[str], prov: str, label: str, groups: dict) -> None:
    lines += [f"## {prov}: {label}", ""]
    for g, body in groups.items():
        lines += [f"### {g} (n={body['n']})", ""]
        if not body["n"]:
            lines += ["No days.", ""]
            continue
        notes = {r["ci_note"] for r in body["comparisons"].values() if r["ci_note"]}
        lines += ["| comparison | W/T/L/mixed | mean diff h>=95F | mean diff h AQI>=101 | mean diff cost |",
                  "|---|---|---|---|---|"]
        for name, r in body["comparisons"].items():
            lines.append(f"| {name} | {_wtl(r)} | {_diff(r, 'hours_ge_95f')} | {_diff(r, 'hours_aqi_ge_101')} "
                         f"| {_diff(r, 'observed_cost')} |")
        lines += [""] + [f"_{n}_" for n in sorted(notes)] + [""]


def to_markdown(res: dict) -> str:
    lines = [res["provenance_statement"], "", "# Madrugada backtest", "",
             f"Days evaluated: {res['n_days']['synthetic']} synthetic, {res['n_days']['real_cached']} real_cached "
             f"(all days with enough history for the proxy forecast; none hand-picked). Runtime "
             f"{res['runtime_seconds']} s.", "",
             "Metrics are modeled exposure-hours scored on observed values; they are not health outcomes.", "",
             "Definitions:"] + [f"- {k}: {v}" for k, v in res["definitions"].items()] + [""]
    for prov in ("synthetic", "real_cached"):
        _group(lines, prov, res["group_labels"][prov], res["groups"][prov])
        lines += [f"### Oracle diagnosis ({prov})", "", res["oracle_diagnosis"][prov]["sentence"], ""]
        for r in res["oracle_diagnosis"][prov]["days"]:
            lines.append(f"- {r['id']}: optimizer {r['optimizer_cost']:g}, B2 {r['B2_cost']:g}, oracle "
                         f"{r['oracle_cost']:g} (oracle vs B2: {r['oracle_vs_B2']})")
        lines += ["", f"### Weight sensitivity ({prov}): optimizer vs B2", "",
                  "| stratum | days | settings | weakly dominates (totals) | strictly improves (totals) "
                  "| weakly dominates (per day) | range total diff h>=95F | range total diff h AQI>=101 |",
                  "|---|---|---|---|---|---|---|---|"]
        for g, w in res["weight_sensitivity"][prov].items():
            if w["n_days"]:
                lines.append(f"| {g} | {w['n_days']} | {w['n_settings']} | {w['weakly_dominates_fraction']:.2f} "
                             f"| {w['strictly_improves_fraction']:.2f} | {w['per_day_weakly_dominates_fraction']:.2f} "
                             f"| {w['range_total_diff_hours_ge_95f']} | {w['range_total_diff_hours_aqi_ge_101']} |")
            else:
                lines.append(f"| {g} | 0 | - | - | - | - | - | - |")
        lines += ["", f"### Forecast-proxy sensitivity ({prov}): optimizer vs B2 (W/T/L/mixed)", "",
                  "| proxy | " + " | ".join(res["forecast_sensitivity"][prov]["default_blend"]) + " |",
                  "|---" * (1 + len(res["forecast_sensitivity"][prov]["default_blend"])) + "|"]
        for name, gs in res["forecast_sensitivity"][prov].items():
            lines.append(f"| {name} | " + " | ".join(f"{_wtl(r)} (n={r['n']})" for r in gs.values()) + " |")
        lines.append("")
    lines += ["## Appendix: every day", "",
              "| day | provenance | stratum | plan | " + " | ".join(PHYS) + " | cost | blocks |",
              "|---" * (len(PHYS) + 6) + "|"]
    for d in res["days"]:
        for p in PLANS:
            m = d["plans"][p]
            lines.append(f"| {d['id']} | {d['provenance']} | {d['stratum']} | {p} | "
                         + " | ".join(f"{m[k]:g}" for k in PHYS) + f" | {m['observed_cost']:g} | "
                         + ", ".join(m["blocks"]) + " |")
        if d["robust_flags"]:
            lines.append(f"| {d['id']} | | | robust flags: {', '.join(d['robust_flags'])} |" + " |" * (len(PHYS) + 2))
    lines += ["", f"Challengers: {', '.join(CHALLENGERS)}. Baselines: {', '.join(BASELINES)}. "
              "'oracle' plans on the day's own observed data: an upper bound, not a forecast.", ""]
    return "\n".join(lines)
