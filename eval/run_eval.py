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
        "definitions": {
            "difference": "challenger minus baseline; negative = fewer modeled exposure-hours or lower cost",
            "tie": f"every physical metric within {cfg['eval']['tie_hours']} h and observed cost within "
                   f"{cfg['eval']['tie_cost']}",
            "win_loss": "by observed weighted cost; 'mixed' = equal cost but different physical metrics",
            "strata": cfg["eval"]["strata"],
            "weight_sensitivity": "stratum totals of (optimizer - B2) hours >=95F and AQI>=101 hours per setting",
        },
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
        r = syn[f"{c}_vs_B2"]
        print(f"synthetic {c} vs B2: W{r['win']} T{r['tie']} L{r['loss']} M{r['mixed']} (n={r['n']})")
    print("oracle diagnosis (synthetic):", results["oracle_diagnosis"]["synthetic"]["sentence"])
    print(f"wrote {j} and {m} in {results['runtime_seconds']} s")


if __name__ == "__main__":
    main()
