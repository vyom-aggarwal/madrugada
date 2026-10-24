"""Markdown rendering of eval results (eval/results.md). First line is the provenance statement."""
from eval.metrics import BASELINES, CHALLENGERS, PHYS, PLANS
from eval.stats import COST_LABEL


def _wtl(r: dict) -> str:
    return f"{r['win']}/{r['tie']}/{r['loss']}/{r['mixed']}"


def _diff(r: dict, k: str) -> str:
    if not r["mean_diff"]:
        return "-"
    ci = r["ci95"][k] if r["ci95"] else None
    return f"{r['mean_diff'][k]:+g}" + (f" [{ci[0]:+g}, {ci[1]:+g}]" if ci else "")


def _outcomes(lines: list[str], groups: dict, kind: str, names: list[str]) -> None:
    strata = list(groups)
    lines += ["| comparison | " + " | ".join(f"{s} (n={groups[s]['n']})" for s in strata) + " |",
              "|---" * (len(strata) + 1) + "|"]
    for name in names:
        cells = [f"{_wtl(c[kind])} (n={c['n']})" if c["n"] else "-"
                 for c in (groups[s]["comparisons"][name] for s in strata)]
        lines.append(f"| {name.replace('_vs_', ' vs ')} | " + " | ".join(cells) + " |")
    lines.append("")


def _inventory(lines: list[str], res: dict) -> None:
    inv = res["real_inventory"]
    lines += ["### Real-data inventory", "", f"- Source path: {inv.get('path')}", f"- {res['effective_sample_size_note']}",
              f"- AirData years: {inv.get('years')}", f"- Days used by region/year: {inv['used_by_region_year']}",
              f"- Excluded by region/year: {inv['excluded_by_region_year']}",
              f"- Exclusion reasons (counts): {inv['excluded_reasons']}", ""]
    for region, src in inv.get("sources", {}).items():
        lines.append(f"- {region}: {src}")
    lines += ["", "Excluded days:", ""] + [
        f"- {e.get('region')} {e.get('date') or e.get('year')}: {'; '.join(e.get('reasons') or [e.get('reason', '')])}"
        for e in inv["excluded"]] + [""]


def _provenance(lines: list[str], res: dict, prov: str) -> None:
    groups = res["groups"][prov]
    lines += [f"## {prov}: {res['group_labels'][prov]} (n={res['n_days'][prov]})", ""]
    if prov == "real_cached":
        lines += [f"Status: {res.get('real_status')}", ""]
    if not res["n_days"][prov]:
        lines += ["No days evaluated.", ""]
        return
    if prov == "real_cached":
        _inventory(lines, res)
    base = [f"{c}_vs_{b}" for c in CHALLENGERS for b in BASELINES]
    same = ["robust_vs_optimizer"] + [f"optimizer_on_robust_days_vs_{b}" for b in BASELINES]
    lines += ["### PRIMARY: physical dominance (W/T/L/mixed)", ""]
    _outcomes(lines, groups, "physical", base)
    fb = res["robust_fallback_days"][prov]
    lines += [f"Robust rows use only days without fallback ({len(fb)} fallback days: {', '.join(fb[:20])}"
              f"{' ...' if len(fb) > 20 else ''}). Same-day comparison with the optimizer:", ""]
    _outcomes(lines, groups, "physical", same)
    lines += [f"### Secondary: cost-based outcomes ({COST_LABEL})", ""]
    _outcomes(lines, groups, "cost", base + same)
    method = next(iter(groups["overall"]["comparisons"].values()))["ci_method"]
    lines += [f"### Mean paired differences, overall (challenger - baseline; 95% CI by {method} where enough)", "",
              "| comparison | n | dates | h>=95F | h AQI>=101 | cost |", "|---|---|---|---|---|---|"]
    for name, r in groups["overall"]["comparisons"].items():
        lines.append(f"| {name} | {r['n']} | {r['n_dates']} | {_diff(r, 'hours_ge_95f')} | {_diff(r, 'hours_aqi_ge_101')} "
                     f"| {_diff(r, 'observed_cost')} |" + (f" {r['ci_note']}" if r["ci_note"] else ""))
    od = res["oracle_diagnosis"][prov]
    lines += ["", "### Oracle diagnosis (optimizer losses to B2)", "",
              f"- Physical (primary): {od['physical']['sentence']}",
              f"- Cost ({COST_LABEL}): {od['cost']['sentence']}", ""]
    losses = res["physical_losses_vs_B2"][prov]
    lines += [f"### Days where the optimizer loses physically to B2 ({len(losses)}; observed numbers)", ""]
    lines += [f"- {x['id']} ({x['stratum']}): optimizer h>=95F {x['optimizer_hours_ge_95f']:g}, AQI>=101 "
              f"{x['optimizer_hours_aqi_ge_101']:g}; B2 h>=95F {x['B2_hours_ge_95f']:g}, AQI>=101 "
              f"{x['B2_hours_aqi_ge_101']:g}" for x in losses] + [""]
    ws = res["weight_sensitivity"][prov]
    lines += ["### Weight sensitivity: optimizer vs B2 (81 settings)", "",
              "| stratum | days | HEADLINE day-level weakly dominates | day-level strictly improves "
              "| totals weakly dominates | totals strictly improves | range total diff h>=95F "
              "| range total diff h AQI>=101 |", "|---" * 8 + "|"]
    for g, w in ws.items():
        if w["n_days"]:
            lines.append(f"| {g} | {w['n_days']} | {w['day_level_weakly_dominates']:.2f} | "
                         f"{w['day_level_strictly_improves']:.2f} | {w['totals_weakly_dominates']:.2f} | "
                         f"{w['totals_strictly_improves']:.2f} | {w['range_total_diff_hours_ge_95f']} | "
                         f"{w['range_total_diff_hours_aqi_ge_101']} |")
    lines += ["", "### Forecast-proxy sensitivity: optimizer vs B2, overall (physical W/T/L/M | cost W/T/L/M)", ""]
    for name, gs in res["forecast_sensitivity"][prov].items():
        o = gs["overall"]
        lines.append(f"- {name} (n={o['n']}): physical {o['physical_win']}/{o['physical_tie']}/{o['physical_loss']}/"
                     f"{o['physical_mixed']} | cost {o['cost_win']}/{o['cost_tie']}/{o['cost_loss']}/{o['cost_mixed']}")
    nc = res["nowcast"][prov]["overall"]
    lines += ["", "### SECONDARY: NowCast-based smoke hours (observed only; mean hours per day, overall)", "",
              "| plan | h AQI>=101 (hourly) | h AQI>=101 (NowCast) | h AQI>=151 (hourly) | h AQI>=151 (NowCast) |",
              "|---|---|---|---|---|"]
    for p in PLANS:
        v = nc[p]
        lines.append(f"| {p} | {v['hours_aqi_ge_101']:g} | {v['nowcast_hours_aqi_ge_101']:g} | "
                     f"{v['hours_aqi_ge_151']:g} | {v['nowcast_hours_aqi_ge_151']:g} |")
    lines.append("")


def to_markdown(res: dict) -> str:
    lines = [res["provenance_statement"], "", "# Madrugada backtest", "", "## What this does and does not show", ""]
    lines += [f"- {s}" for s in res["summary_box"]] + ["", f"Runtime {res['runtime_seconds']} s.", "", "Definitions:"]
    lines += [f"- {k}: {v}" for k, v in res["definitions"].items()] + [""]
    for prov in ("synthetic", "real_cached"):
        _provenance(lines, res, prov)
    lines += ["## Appendix: every day", "",
              "| day | provenance | stratum | sources | plan | " + " | ".join(PHYS) + " | cost | blocks |",
              "|---" * (len(PHYS) + 7) + "|"]
    for d in res["days"]:
        src = "; ".join(f"{k}: {v}" for k, v in (d.get("sources") or {}).items()) or "synthetic"
        for p in PLANS:
            m = d["plans"][p]
            note = " (robust fell back)" if p == "robust" and d["robust_flags"] else ""
            lines.append(f"| {d['id']} | {d['provenance']} | {d['stratum']} | {src} | {p}{note} | "
                         + " | ".join(f"{m[k]:g}" for k in PHYS) + f" | {m['observed_cost']:g} | "
                         + ", ".join(m["blocks"]) + " |")
    lines += ["", f"Challengers: {', '.join(CHALLENGERS)}. Baselines: {', '.join(BASELINES)}. "
              "'oracle' plans on the day's own observed data: an upper bound, not a forecast.", ""]
    return "\n".join(lines)
