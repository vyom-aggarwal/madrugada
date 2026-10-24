"""Backtest: plan every evaluable day, score on observed values, aggregate, write results.json/.md.

Run: python eval/run_eval.py
Synthetic and real_cached days are evaluated and reported separately, never pooled.
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import load_config  # noqa: E402
from app.exposure import day_arrays  # noqa: E402
from app.planning import load_days  # noqa: E402
from eval import metrics, stats  # noqa: E402
from eval.report import to_markdown  # noqa: E402

OUT_DIR = ROOT / "eval"
PROVENANCES = ("synthetic", "real_cached")
SYNTHETIC_STATEMENT = "SYNTHETIC DAYS INCLUDED: NOT EVIDENCE FOR THE DUAL-HAZARD CLAIM"


def provenance_statement(n_syn: int, n_real: int, min_real: int) -> str:
    parts = []
    if n_syn:
        parts.append(SYNTHETIC_STATEMENT)
    if n_real < min_real:
        parts.append(f"insufficient real days ({n_real} real_cached, {min_real} required)")
    return " | ".join(parts) if parts else f"REAL DAYS ONLY ({n_real} real_cached days)"


def summary_box(by_prov: dict, cfg: dict) -> list[str]:
    """Plain 'What this does and does not show' lines, generated from the data."""
    syn, real = by_prov["synthetic"], by_prov["real_cached"]
    n_hist = sum("history" in d["label"].lower() for d in syn)
    lines = [f"Days evaluated: {len(syn) + len(real)} ({len(syn)} synthetic, {len(real)} real_cached); every day "
             "with enough history for the forecast proxy, none hand-picked."]
    if syn:
        lines.append(f"The {len(syn)} synthetic days ({n_hist} of them generated history days) are illustrations: they "
                     "show how the planner behaves, not that it reduces exposure in the field.")
    if len(real) < cfg["eval"]["min_real_days"]:
        lines.append(f"insufficient real days: {len(real)} real_cached, {cfg['eval']['min_real_days']} required for "
                     "any real-data conclusion. This page shows no real-data result.")
    lines.append("Heat-only planning is the closest baseline; see the B3 rows.")
    for prov, ds in (("synthetic", syn), ("real_cached", real)):
        if not ds:
            continue
        w = stats.b3_smoke_wins(ds, cfg)
        if not any(w.values()):
            lines.append(f"In the current {prov} data the optimizer never has fewer AQI>=101 hours than either B3 "
                         f"variant (0 of {len(ds)} days).")
        else:
            lines.append(f"{prov}: the optimizer has fewer AQI>=101 hours than b3_early on {w['b3_early']} and than "
                         f"b3_late on {w['b3_late']} of {len(ds)} days.")
    lines.append("Numbers are modeled exposure-hours from station-level data. They are not health outcomes, not "
                 "field microclimate, and not a compliance assessment.")
    return lines


def run(pool=None, cfg: dict | None = None) -> dict:
    t0 = time.perf_counter()
    cfg = cfg or load_config()
    pool = list(pool if pool is not None else load_days())
    days = metrics.evaluable(pool, cfg)
    per_day = [metrics.evaluate_day(d, pool, cfg) for d in days]
    by_prov = {p: [d for d in per_day if d["provenance"] == p] for p in PROVENANCES}

    sens_inputs = []
    for d, rec in zip(days, per_day):
        ft, fa = metrics.forecast_arrays(d, pool, cfg)
        ot, oa = day_arrays(d)
        sens_inputs.append({"id": d.id, "stratum": rec["stratum"], "provenance": d.provenance,
                            "ft": ft, "fa": fa, "ot": ot, "oa": oa})
    weight_rows = metrics.weight_sensitivity(sens_inputs, cfg)
    fc_rows = metrics.forecast_sensitivity(days, pool, cfg)

    n_syn, n_real = len(by_prov["synthetic"]), len(by_prov["real_cached"])
    min_real = cfg["eval"]["min_real_days"]
    results = {
        "provenance_statement": provenance_statement(n_syn, n_real, min_real),
        "n_days": {"synthetic": n_syn, "real_cached": n_real},
        "real_days_sufficient": n_real >= min_real,
        "group_labels": {"synthetic": "SYNTHETIC, NOT EVIDENCE",
                         "real_cached": "REAL (cached)" if n_real >= min_real else "insufficient real days"},
        "summary_box": summary_box(by_prov, cfg),
        "definitions": {
            "primary_outcome": "physical dominance: win = no more hours >=95F and no more AQI>=101 hours and "
                               "strictly less on at least one; loss = the reverse; tie = all physical metrics "
                               f"within {cfg['eval']['tie_hours']} h; otherwise mixed",
            "secondary_outcome": f"{stats.COST_LABEL}: win/loss by observed weighted cost; tie also needs cost "
                                 f"within {cfg['eval']['tie_cost']}; mixed = equal cost, different physical metrics",
            "difference": "challenger minus baseline; negative = fewer modeled exposure-hours or lower cost",
            "robust": "compared only on days where it did not fall back; fallback days listed separately",
            "strata": cfg["eval"]["strata"],
            "weight_sensitivity": "headline = day-level fraction of (setting, day) pairs; stratum totals secondary",
        },
        "robust_fallback_days": {p: [d["id"] for d in by_prov[p] if d["robust_flags"]] for p in PROVENANCES},
        "groups": {p: stats.group_summary(by_prov[p], cfg) for p in PROVENANCES},
        "oracle_diagnosis": {p: stats.oracle_diagnosis(by_prov[p], cfg) for p in PROVENANCES},
        "weight_sensitivity": {p: stats.weight_summary(weight_rows, p) for p in PROVENANCES},
        "forecast_sensitivity": {p: {name: stats.outcome_counts(rows, p) for name, rows in fc_rows.items()}
                                 for p in PROVENANCES},
        "days": per_day,
    }
    results["runtime_seconds"] = round(time.perf_counter() - t0, 2)
    return results


def write(results: dict, out_dir: Path = OUT_DIR) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    j, m = out_dir / "results.json", out_dir / "results.md"
    j.write_text(json.dumps(results, indent=1), encoding="utf-8")
    m.write_text(to_markdown(results), encoding="utf-8")
    return j, m


def main() -> None:
    results = run()
    j, m = write(results)
    print(results["provenance_statement"])
    syn = results["groups"]["synthetic"]["overall"]["comparisons"]
    for c in metrics.CHALLENGERS:
        for b in ("B2", "b3_early", "b3_late"):
            r = syn[f"{c}_vs_{b}"]
            p, k = r["physical"], r["cost"]
            print(f"synthetic {c} vs {b} (n={r['n']}): physical W{p['win']} T{p['tie']} L{p['loss']} M{p['mixed']}"
                  f" | cost W{k['win']} T{k['tie']} L{k['loss']} M{k['mixed']}")
    od = results["oracle_diagnosis"]["synthetic"]
    print("oracle diagnosis (synthetic, physical):", od["physical"]["sentence"])
    print("oracle diagnosis (synthetic, cost):", od["cost"]["sentence"])
    ws = results["weight_sensitivity"]["synthetic"]
    print("day-level weak dominance vs B2:", {g: v.get("day_level_weakly_dominates") for g, v in ws.items()})
    print(f"wrote {j} and {m} in {results['runtime_seconds']} s")


if __name__ == "__main__":
    main()
