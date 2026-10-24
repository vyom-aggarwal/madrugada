"""Aggregation: win/tie/loss counts, mean paired differences, paired bootstrap CIs (numpy only)."""
import numpy as np

from eval.metrics import BASELINES, CHALLENGERS, STRATA, classify

DIFF_KEYS = ("hours_ge_95f", "hours_aqi_ge_101", "observed_cost")
OUTCOMES = ("win", "tie", "loss", "mixed")
CI_NOTE = "n too small for CIs"


def paired_bootstrap_ci(diffs, resamples: int, seed: int) -> tuple[float, float]:
    """95% percentile CI of the mean of paired differences. Deterministic for a fixed seed."""
    d = np.asarray(diffs, dtype=float)
    idx = np.random.default_rng(seed).integers(0, len(d), size=(resamples, len(d)))
    lo, hi = np.percentile(d[idx].mean(axis=1), [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


def compare(days: list[dict], challenger: str, baseline: str, cfg: dict) -> dict:
    """challenger - baseline over `days` (paired). Negative differences favour the challenger."""
    bs = cfg["eval"]["bootstrap"]
    counts = {o: 0 for o in OUTCOMES}
    for d in days:
        counts[classify(d["plans"][challenger], d["plans"][baseline], cfg)] += 1
    out = {"n": len(days), **counts, "mean_diff": {}, "ci95": None, "ci_note": None}
    if not days:
        return out
    diffs = {k: [d["plans"][challenger][k] - d["plans"][baseline][k] for d in days] for k in DIFF_KEYS}
    out["mean_diff"] = {k: round(float(np.mean(v)), 4) for k, v in diffs.items()}
    if len(days) < bs["min_n"]:
        out["ci_note"] = CI_NOTE
    else:
        out["ci95"] = {k: paired_bootstrap_ci(v, bs["resamples"], bs["seed"]) for k, v in diffs.items()}
    return out


def group_summary(days: list[dict], cfg: dict) -> dict:
    """By stratum and overall: every challenger vs every baseline."""
    groups = {"overall": days, **{s: [d for d in days if d["stratum"] == s] for s in STRATA}}
    return {g: {"n": len(ds), "comparisons": {f"{c}_vs_{b}": compare(ds, c, b, cfg)
                                              for c in CHALLENGERS for b in BASELINES}}
            for g, ds in groups.items()}


def oracle_diagnosis(days: list[dict], cfg: dict) -> dict:
    """For each day the optimizer loses to B2 on observed cost: does the oracle optimizer beat B2?"""
    rows = []
    for d in days:
        if classify(d["plans"]["optimizer"], d["plans"]["B2"], cfg) == "loss":
            oracle = classify(d["plans"]["oracle"], d["plans"]["B2"], cfg)
            rows.append({"id": d["id"], "optimizer_cost": d["plans"]["optimizer"]["observed_cost"],
                         "B2_cost": d["plans"]["B2"]["observed_cost"],
                         "oracle_cost": d["plans"]["oracle"]["observed_cost"],
                         "oracle_vs_B2": oracle, "oracle_beats_B2": oracle == "win"})
    gone = sum(r["oracle_vs_B2"] != "loss" for r in rows)
    return {"sentence": f"{gone} of {len(rows)} losses disappear under the oracle.", "days": rows}


def weight_summary(rows: list[dict], provenance: str) -> dict:
    """Per stratum (and overall): fraction of settings where optimizer totals weakly dominate B2
    (no more hours >=95F and no more AQI>=101 hours, summed over the stratum's days), fraction where it
    strictly improves one without worsening the other, and the range of total differences."""
    out = {}
    for g in ("overall",) + STRATA:
        totals, pairs = [], []
        for r in rows:
            ds = [d for d in r["days"] if d["provenance"] == provenance and (g == "overall" or d["stratum"] == g)]
            if ds:
                totals.append((sum(d["d95"] for d in ds), sum(d["d101"] for d in ds), len(ds)))
                pairs += [d["d95"] <= 1e-9 and d["d101"] <= 1e-9 for d in ds]
        if not totals:
            out[g] = {"n_days": 0, "n_settings": 0}
            continue
        t = np.array([x[:2] for x in totals])
        weak = (t[:, 0] <= 1e-9) & (t[:, 1] <= 1e-9)
        strict = weak & ((t[:, 0] < -1e-9) | (t[:, 1] < -1e-9))
        out[g] = {"n_days": totals[0][2], "n_settings": len(totals),
                  "weakly_dominates_fraction": round(float(weak.mean()), 4),
                  "strictly_improves_fraction": round(float(strict.mean()), 4),
                  "per_day_weakly_dominates_fraction": round(float(np.mean(pairs)), 4),  # over (setting, day) pairs
                  "range_total_diff_hours_ge_95f": [round(float(t[:, 0].min()), 4), round(float(t[:, 0].max()), 4)],
                  "range_total_diff_hours_aqi_ge_101": [round(float(t[:, 1].min()), 4), round(float(t[:, 1].max()), 4)]}
    return out


def outcome_counts(rows: list[dict], provenance: str) -> dict:
    out = {}
    for g in ("overall",) + STRATA:
        ds = [r for r in rows if r["provenance"] == provenance and (g == "overall" or r["stratum"] == g)]
        out[g] = {"n": len(ds), **{o: sum(r["outcome"] == o for r in ds) for o in OUTCOMES}}
    return out
