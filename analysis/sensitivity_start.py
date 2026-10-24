"""EXPLORATORY, POST-HOC: not preregistered. Non-logic. Start-time sensitivity: re-plan the optimizer and the
oracle with earliest_start in {04:00 .. 06:00} and a sunrise-aligned rule, compare with B2 and with B_sun (a fixed
shift starting at that setting's earliest start), and split the effect into "one block placed earlier" vs
"splitting into two blocks". Reuses the frozen functions read-only; uses the global config unmodified.

Run: python -m analysis.sensitivity_start   (window 1; analysis/eval_window2.py calls run() for window 2)
"""
import json
import math
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.baselines import b2  # noqa: E402
from app.config import load_config  # noqa: E402
from app.exposure import day_arrays, hhmm_to_slot, slot_to_hhmm  # noqa: E402
from app.models import Block, DayRecord  # noqa: E402
from app.optimizer import hours_to_slots, optimize  # noqa: E402
from eval.metrics import STRATA, forecast_arrays, score  # noqa: E402
from eval.run_eval import _pool_of  # noqa: E402
from eval.stats import cluster_bootstrap_ci, compare  # noqa: E402

LABEL = "EXPLORATORY, POST-HOC: not preregistered"
SETTINGS = ["04:00", "04:30", "05:00", "05:30", "06:00", "sunrise"]
COMPS = [("optimizer", "B2"), ("optimizer", "B_sun"), ("oracle", "B2"), ("oracle", "B_sun"),
         ("optimizer_1block", "B2"), ("optimizer", "optimizer_1block")]
FALLBACK = {"bakersfield": (35.37, -119.02), "fresno": (36.74, -119.79), "tulare": (36.33, -119.29)}
LA = ZoneInfo("America/Los_Angeles")


def sunrise_local(day: date, lat: float, lon: float) -> datetime:
    """APPROXIMATE, UNVERIFIED: NOAA general solar-position equations (fractional year at noon, zenith 90.833 deg)."""
    g = 2 * math.pi / 365 * (day.timetuple().tm_yday - 1)
    c, s = math.cos, math.sin
    eqt = 229.18 * (0.000075 + 0.001868 * c(g) - 0.032077 * s(g) - 0.014615 * c(2 * g) - 0.040849 * s(2 * g))
    decl = (0.006918 - 0.399912 * c(g) + 0.070257 * s(g) - 0.006758 * c(2 * g) + 0.000907 * s(2 * g)
            - 0.002697 * c(3 * g) + 0.00148 * s(3 * g))
    la = math.radians(lat)
    ha = math.degrees(math.acos(math.cos(math.radians(90.833)) / (math.cos(la) * math.cos(decl))
                                - math.tan(la) * math.tan(decl)))
    utc = datetime(day.year, day.month, day.day, tzinfo=timezone.utc) + timedelta(minutes=720 - 4 * (lon + ha) - eqt)
    return utc.astimezone(LA)


def sunrise_start(day: date, lat: float, lon: float, cfg: dict) -> str:
    """Sunrise minus 30 minutes, rounded to the nearest grid slot."""
    t = sunrise_local(day, lat, lon) - timedelta(minutes=30)
    step = cfg["grid"]["slot_minutes"]
    m = round((t.hour * 60 + t.minute + t.second / 60) / step) * step
    return f"{m // 60:02d}:{m % 60:02d}"


def coords(manifest_path: Path) -> dict:
    """Station lat/lon per region: day metadata has none, so the job manifest, else the fixed fallback."""
    m = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    out = {}
    for region, fb in FALLBACK.items():
        a = (m.get("sources", {}).get(region) or {}).get("asos") or {}
        out[region] = (a["lat"], a["lon"], "manifest") if a.get("lat") is not None else (*fb, "fallback")
    return out


def day_rows(d: DayRecord, pool: list, cfg: dict, latlon: dict) -> dict:
    ft, fa = forecast_arrays(d, pool, cfg)
    ot, oa = day_arrays(d)
    base_b2 = score(b2(ft, fa, cfg=cfg).blocks, ot, oa, cfg)
    n_paid = hours_to_slots(cfg["shift"]["default_paid_hours"], cfg)
    out = {}
    for s in SETTINGS:
        e = sunrise_start(date.fromisoformat(d.date), *latlon[d.region][:2], cfg) if s == "sunrise" else s
        opt = optimize(ft, fa, earliest_start=e, cfg=cfg)
        one = optimize(ft, fa, earliest_start=e, max_blocks=1, cfg=cfg)
        orc = optimize(ot, oa, earliest_start=e, cfg=cfg, name="oracle")
        e0 = hhmm_to_slot(e, cfg)
        b = opt.blocks
        out[s] = {"earliest": e, "start": slot_to_hhmm(b[0].start_slot, cfg), "n_blocks": len(b),
                  "gap_h": (b[1].start_slot - b[0].end_slot) * cfg["grid"]["slot_minutes"] / 60 if len(b) == 2 else None,
                  "plans": {"optimizer": score(b, ot, oa, cfg), "optimizer_1block": score(one.blocks, ot, oa, cfg),
                            "oracle": score(orc.blocks, ot, oa, cfg), "B2": base_b2,
                            "B_sun": score([Block(start_slot=e0, end_slot=e0 + n_paid)], ot, oa, cfg)}}
    return out


def summarize(rows: list[dict], cfg: dict) -> dict:
    bs = cfg["eval"]["bootstrap"]
    res = {}
    for s in SETTINGS:
        recs = [{"id": r["id"], "date": r["date"], "stratum": r["stratum"], "plans": r["by"][s]["plans"]} for r in rows]
        groups = {"overall": recs, **{g: [x for x in recs if x["stratum"] == g] for g in STRATA}}
        per = {}
        for g, ds in groups.items():
            per[g] = {}
            for c, b in COMPS:
                x = compare(ds, c, b, cfg, cluster=True)
                d80 = [d["plans"][c]["hours_ge_80f"] - d["plans"][b]["hours_ge_80f"] for d in ds]
                ok = x["n_dates"] >= bs["min_n"]
                per[g][f"{c}_vs_{b}"] = {
                    "n": x["n"], "n_dates": x["n_dates"], "physical": x["physical"],
                    "mean_diff": {**{k: x["mean_diff"].get(k) for k in ("hours_ge_95f", "hours_aqi_ge_101")},
                                  "hours_ge_80f": round(float(np.mean(d80)), 4) if ds else None},
                    "ci95": {"hours_ge_95f": x["ci95"]["hours_ge_95f"], "hours_aqi_ge_101": x["ci95"]["hours_aqi_ge_101"],
                             "hours_ge_80f": cluster_bootstrap_ci(d80, [d["date"] for d in ds], bs["resamples"], bs["seed"])}
                    if ok else None}
        info = [r["by"][s] for r in rows]
        gaps = [i["gap_h"] for i in info if i["gap_h"] is not None]
        res[s] = {"groups": per, "start_times": dict(sorted(Counter(i["start"] for i in info).items())),
                  "earliest_values": dict(sorted(Counter(i["earliest"] for i in info).items())),
                  "share_two_blocks": round(len(gaps) / len(info), 4) if info else None,
                  "median_gap_h": float(np.median(gaps)) if gaps else None,
                  "mean_h95": {p: round(float(np.mean([i["plans"][p]["hours_ge_95f"] for i in info])), 4)
                               for p in ("B2", "B_sun", "optimizer", "oracle")} if info else {}}
    return res


def run(day_ids: list[str], records: dict, manifest_path: Path, cfg: dict | None = None) -> dict:
    cfg = cfg or load_config()
    latlon = coords(manifest_path)
    pool_of = _pool_of(list(records.values()))
    rows = []
    for i in day_ids:
        d = records[i]
        ot, oa = day_arrays(d)
        from eval.metrics import stratum
        rows.append({"id": i, "date": d.date, "stratum": stratum(ot, oa, cfg), "by": day_rows(d, pool_of(d), cfg, latlon)})
    return {"label": LABEL, "n_days": len(rows), "n_dates": len({r["date"] for r in rows}),
            "coords": {k: list(v) for k, v in latlon.items()}, "settings": summarize(rows, cfg)}


def main() -> dict:
    from app.planning import load_days
    res = json.loads((ROOT / "eval" / "results.json").read_text(encoding="utf-8"))
    ids = [d["id"] for d in res["days"] if d["provenance"] == "real_cached"]
    records = {d.id: d for d in load_days() if d.provenance == "real_cached"}
    out = run(ids, records, ROOT / "data" / "cache" / "meta" / "manifest.json")
    path = ROOT / "analysis" / "start_sensitivity.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{LABEL}: wrote {path} ({out['n_days']} region-days)")
    return out


if __name__ == "__main__":
    main()
