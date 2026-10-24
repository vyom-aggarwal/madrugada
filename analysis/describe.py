"""EXPLORATORY, POST-HOC: not preregistered. Non-logic: reads eval/results.json and the real cache, reuses the
frozen functions read-only, and writes analysis/exploratory_results.json. Never edits hashed files.

Run: python -m analysis.describe
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.baselines import b3_early  # noqa: E402
from app.config import load_config  # noqa: E402
from app.exposure import day_arrays, exposure, hazard_flags  # noqa: E402
from app.planning import load_days  # noqa: E402
from eval.metrics import STRATA, classify_physical  # noqa: E402
from eval.stats import cluster_bootstrap_ci  # noqa: E402

RESULTS = ROOT / "eval" / "results.json"
OUT = ROOT / "analysis" / "exploratory_results.json"
LABEL = "EXPLORATORY, POST-HOC: not preregistered"


def _q(v, q):
    return round(float(np.percentile(v, q)), 3) if len(v) else None


def whole_day(rec) -> dict:
    t, a = day_arrays(rec)
    m = exposure(t, a, np.ones(len(t), bool))
    return {"h95": m.hours_ge_95f, "h101": m.hours_aqi_ge_101, "h151": m.hours_aqi_ge_151}


def strata_inventory(days, hz) -> dict:
    out = {"by_stratum": {}, "by_region": {}, "by_year": {}}
    for s in STRATA:
        ds = [d for d in days if d["stratum"] == s]
        out["by_stratum"][s] = {"days": len(ds), "dates": len({d["date"] for d in ds})}
    for key, f in (("by_region", lambda d: d["region"]), ("by_year", lambda d: d["date"][:4])):
        for k in sorted({f(d) for d in days}):
            out[key][k] = dict(Counter(d["stratum"] for d in days if f(d) == k))
    out["days_any_aqi101"] = sum(hz[d["id"]]["h101"] > 0 for d in days)
    out["days_any_aqi151"] = sum(hz[d["id"]]["h151"] > 0 for d in days)
    out["total_hours_aqi101"] = round(sum(hz[d["id"]]["h101"] for d in days), 2)
    out["total_hours_aqi151"] = round(sum(hz[d["id"]]["h151"] for d in days), 2)
    return out


def effect_by_stratum(days, cfg) -> dict:
    bs = cfg["eval"]["bootstrap"]
    out = {}
    for base in ("B2", "b3_late"):
        for g in ("overall",) + STRATA:
            ds = [d for d in days if g == "overall" or d["stratum"] == g]
            dates = [d["date"] for d in ds]
            row = {"n": len(ds), "dates": len(set(dates))}
            for k in ("hours_ge_95f", "hours_ge_80f", "hours_aqi_ge_101"):
                diff = [d["plans"]["optimizer"][k] - d["plans"][base][k] for d in ds]
                row[k] = {"mean": round(float(np.mean(diff)), 4) if ds else None,
                          "ci95": cluster_bootstrap_ci(diff, dates, bs["resamples"], bs["seed"])
                          if len(set(dates)) >= bs["min_n"] else None}
            out[f"optimizer_vs_{base}|{g}"] = row
    return out


def mixed_anatomy(days, cfg) -> dict:
    out = {}
    for g in ("overall",) + STRATA:
        mixed = [d for d in days if (g == "overall" or d["stratum"] == g)
                 and classify_physical(d["plans"]["optimizer"], d["plans"]["B2"], cfg) == "mixed"]
        d95 = np.array([d["plans"]["optimizer"]["hours_ge_95f"] - d["plans"]["B2"]["hours_ge_95f"] for d in mixed])
        d101 = np.array([d["plans"]["optimizer"]["hours_aqi_ge_101"] - d["plans"]["B2"]["hours_aqi_ge_101"] for d in mixed])
        hd_su, hu_sd = (d95 < 0) & (d101 > 0), (d95 > 0) & (d101 < 0)
        same = (d95 == 0) & (d101 == 0)
        out[g] = {"mixed_days": len(mixed), "heat_down_smoke_up": int(hd_su.sum()), "heat_up_smoke_down": int(hu_sd.sum()),
                  "95F_and_AQI101_unchanged_other_metric_differs": int(same.sum()),
                  "heat_down_smoke_up_change_h95": {"median": _q(-d95[hd_su], 50), "p90": _q(-d95[hd_su], 90)},
                  "heat_down_smoke_up_change_h101": {"median": _q(d101[hd_su], 50), "p90": _q(d101[hd_su], 90)},
                  "heat_up_smoke_down_change_h95": {"median": _q(d95[hu_sd], 50), "p90": _q(d95[hu_sd], 90)},
                  "heat_up_smoke_down_change_h101": {"median": _q(-d101[hu_sd], 50), "p90": _q(-d101[hu_sd], 90)}}
        if mixed:
            other = [d for d, s in zip(mixed, same) if s]
            d80 = [d["plans"]["optimizer"]["hours_ge_80f"] - d["plans"]["B2"]["hours_ge_80f"] for d in other]
            out[g]["unchanged_case_change_h80"] = {"median": _q(d80, 50), "p10": _q(d80, 10), "p90": _q(d80, 90)}
    return out


def smoke_movability(days, recs, hz, cfg) -> dict:
    smoky = [d for d in days if hz[d["id"]]["h101"] >= 1.0]
    removed = np.array([d["plans"]["B2"]["hours_aqi_ge_101"] - d["plans"]["oracle"]["hours_aqi_ge_101"] for d in smoky])
    heat_added = np.array([d["plans"]["oracle"]["hours_ge_95f"] - d["plans"]["B2"]["hours_ge_95f"] for d in smoky])
    inside = outside_win = outside_allowed = 0.0
    split = Counter()
    lo, hi = (int(cfg["shift"][k][:2]) * 4 for k in ("default_earliest_start", "default_latest_end"))
    for d in smoky:
        t, a = day_arrays(recs[d["id"]])
        smoke = hazard_flags(t, a)["aqi_ge_101"]
        mask = np.zeros(len(t), bool)
        for b in b3_early(t, a).blocks:  # heat-only optimizer on OBSERVED data = heat-optimal window
            mask[b.start_slot:b.end_slot] = True
        allowed = np.zeros(len(t), bool)
        allowed[lo:hi] = True
        i, o = (smoke & mask).sum() / 4, (smoke & ~mask & allowed).sum() / 4
        inside, outside_win, outside_allowed = inside + i, outside_win + o, outside_allowed + (smoke & ~allowed).sum() / 4
        split["all inside" if i and not o else "all outside" if o and not i else "split" if i else "none in shift hours"] += 1
    return {"smoke_days": len(smoky), "oracle_removed_h101_vs_B2": {"total": round(float(removed.sum()), 2),
            "mean": round(float(removed.mean()), 3) if len(smoky) else None, "median": _q(removed, 50),
            "days_any_removed": int((removed > 0).sum())},
            "oracle_added_h95_vs_B2": {"total": round(float(heat_added.sum()), 2),
                                       "mean": round(float(heat_added.mean()), 3) if len(smoky) else None},
            "smoke_hours_inside_heat_optimal_window": inside, "smoke_hours_outside_window_in_allowed_hours": outside_win,
            "smoke_hours_outside_allowed_hours": outside_allowed, "days_by_location_within_allowed_hours": dict(split)}


def time_of_day(days, recs) -> dict:
    out = {}
    for g in ("overall",) + STRATA:
        ds = [recs[d["id"]] for d in days if g == "overall" or d["stratum"] == g]
        if not ds:
            continue
        aqi = np.mean([day_arrays(r)[1][::4] for r in ds], axis=0)
        temp = np.mean([np.asarray(r.temp_f)[::4] for r in ds], axis=0)
        out[g] = {"n": len(ds), "mean_aqi_by_hour": [round(float(x), 1) for x in aqi],
                  "mean_temp_by_hour": [round(float(x), 1) for x in temp],
                  "cleanest_hours": [int(h) for h in np.argsort(aqi)[:3]], "coolest_hours": [int(h) for h in np.argsort(temp)[:3]],
                  "dirtiest_hours": [int(h) for h in np.argsort(aqi)[-3:][::-1]], "hottest_hours": [int(h) for h in np.argsort(temp)[-3:][::-1]]}
    return out


def main() -> dict:
    cfg = load_config()
    res = json.loads(RESULTS.read_text(encoding="utf-8"))
    days = [d for d in res["days"] if d["provenance"] == "real_cached"]
    recs = {d.id: d for d in load_days() if d.provenance == "real_cached"}
    days = [d for d in days if d["id"] in recs]
    hz = {d["id"]: whole_day(recs[d["id"]]) for d in days}
    out = {"label": LABEL, "n_days": len(days), "n_dates": len({d["date"] for d in days}),
           "strata_inventory": strata_inventory(days, hz), "effect_by_stratum": effect_by_stratum(days, cfg),
           "mixed_anatomy": mixed_anatomy(days, cfg), "smoke_movability": smoke_movability(days, recs, hz, cfg),
           "time_of_day": time_of_day(days, recs)}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{LABEL}: wrote {OUT} ({len(days)} real region-days)")
    return out


if __name__ == "__main__":
    main()
