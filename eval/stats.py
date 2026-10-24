"""Aggregation: physical-dominance (primary) and cost (secondary) outcomes, mean paired differences,
paired bootstrap CIs (numpy only), oracle diagnosis, sensitivity summaries."""
import numpy as np

from eval.metrics import BASELINES, CHALLENGERS, STRATA, classify, classify_physical

DIFF_KEYS = ("hours_ge_95f", "hours_aqi_ge_101", "observed_cost")
OUTCOMES = ("win", "tie", "loss", "mixed")
CI_NOTE = "n too small for CIs"
COST_LABEL = "uses the optimizer's own cost"


def paired_bootstrap_ci(diffs, resamples: int, seed: int) -> tuple[float, float]:
    """95% percentile CI of the mean of paired differences. Deterministic for a fixed seed."""
    d = np.asarray(diffs, dtype=float)
    idx = np.random.default_rng(seed).integers(0, len(d), size=(resamples, len(d)))
    lo, hi = np.percentile(d[idx].mean(axis=1), [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


def compare(days: list[dict], challenger: str, baseline: str, cfg: dict) -> dict:
    """challenger - baseline over `days` (paired). Negative differences favour the challenger."""
    bs = cfg["eval"]["bootstrap"]
    phys, cost = {o: 0 for o in OUTCOMES}, {o: 0 for o in OUTCOMES}
    for d in days:
        a, b = d["plans"][challenger], d["plans"][baseline]
        phys[classify_physical(a, b, cfg)] += 1
        cost[classify(a, b, cfg)] += 1
    out = {"n": len(days), "physical": phys, "cost": cost, "mean_diff": {}, "ci95": None, "ci_note": None}
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
    """By stratum and overall: every challenger vs every baseline. Robust is compared only on days where
    it did not fall back (its n is shown per comparison)."""
    groups = {"overall": days, **{s: [d for d in days if d["stratum"] == s] for s in STRATA}}
    out = {}
    for g, ds in groups.items():
        comps = {}
        for c in CHALLENGERS:
            cds = [d for d in ds if not d["robust_flags"]] if c == "robust" else ds
            for b in BASELINES:
                comps[f"{c}_vs_{b}"] = compare(cds, c, b, cfg)
        out[g] = {"n": len(ds), "comparisons": comps}
    return out


def oracle_diagnosis(days: list[dict], cfg: dict) -> dict:
    """For each day the optimizer loses to B2 (physical = primary, cost = secondary): how does the oracle do?"""
    out = {}
    for kind, fn in (("physical", classify_physical), ("cost", classify)):
        rows = []
        for d in days:
            p = d["plans"]
            if fn(p["optimizer"], p["B2"], cfg) == "loss":
                rows.append({"id": d["id"], "oracle_vs_B2": fn(p["oracle"], p["B2"], cfg),
                             **{f"{n}_{k}": p[n][k] for n in ("optimizer", "B2", "oracle") for k in DIFF_KEYS}})
        wins = sum(r["oracle_vs_B2"] == "win" for r in rows)
        ties = sum(r["oracle_vs_B2"] == "tie" for r in rows)
        rest = len(rows) - wins - ties
        sentence = f"{wins} of {len(rows)} losses become oracle wins, {ties} become ties"
        out[kind] = {"sentence": sentence + (f"; {rest} remain losses or mixed." if rest else "."), "days": rows,
                     "oracle_wins": wins, "oracle_ties": ties, "losses": len(rows)}
    out["cost"]["label"] = COST_LABEL
    return out


def weight_summary(rows: list[dict], provenance: str) -> dict:
    """Optimizer vs B2 across weight settings. HEADLINE (day-level): fraction of (setting, day) pairs where
    the optimizer has no more hours >=95F and no more AQI>=101 hours (weak), and also strictly less on one
    (strict). SECONDARY: the same on stratum totals per setting, and the range of total differences."""
    out = {}
    for g in ("overall",) + STRATA:
        totals, weak_pairs, strict_pairs = [], [], []
        for r in rows:
            ds = [d for d in r["days"] if d["provenance"] == provenance and (g == "overall" or d["stratum"] == g)]
            if ds:
                totals.append((sum(d["d95"] for d in ds), sum(d["d101"] for d in ds), len(ds)))
                for d in ds:
                    weak = d["d95"] <= 1e-9 and d["d101"] <= 1e-9
                    weak_pairs.append(weak)
                    strict_pairs.append(weak and (d["d95"] < -1e-9 or d["d101"] < -1e-9))
        if not totals:
            out[g] = {"n_days": 0, "n_settings": 0}
            continue
        t = np.array([x[:2] for x in totals])
        weak = (t[:, 0] <= 1e-9) & (t[:, 1] <= 1e-9)
        strict = weak & ((t[:, 0] < -1e-9) | (t[:, 1] < -1e-9))
        out[g] = {"n_days": totals[0][2], "n_settings": len(totals),
                  "day_level_weakly_dominates": round(float(np.mean(weak_pairs)), 4),
                  "day_level_strictly_improves": round(float(np.mean(strict_pairs)), 4),
                  "totals_weakly_dominates": round(float(weak.mean()), 4),
                  "totals_strictly_improves": round(float(strict.mean()), 4),
                  "range_total_diff_hours_ge_95f": [round(float(t[:, 0].min()), 4), round(float(t[:, 0].max()), 4)],
                  "range_total_diff_hours_aqi_ge_101": [round(float(t[:, 1].min()), 4), round(float(t[:, 1].max()), 4)]}
    return out


def outcome_counts(rows: list[dict], provenance: str) -> dict:
    out = {}
    for g in ("overall",) + STRATA:
        ds = [r for r in rows if r["provenance"] == provenance and (g == "overall" or r["stratum"] == g)]
        out[g] = {"n": len(ds), **{f"{kind}_{o}": sum(r[kind] == o for r in ds)
                                   for kind in ("physical", "cost") for o in OUTCOMES}}
    return out


def b3_smoke_wins(days: list[dict], cfg: dict) -> dict:
    """Days where the optimizer has fewer AQI>=101 hours than each B3 variant (by at least tie_hours)."""
    th = cfg["eval"]["tie_hours"]
    return {b: sum(d["plans"][b]["hours_aqi_ge_101"] - d["plans"]["optimizer"]["hours_aqi_ge_101"] >= th
                   for d in days) for b in ("b3_early", "b3_late")}
