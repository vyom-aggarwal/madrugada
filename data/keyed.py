"""Keyed real-data path: CIMIS (CIMIS_APPKEY) + AirNow (AIRNOW_KEY). Used by tasks.py real when both
keys are set. Moved unchanged from data/real_job.py (phase 5); the orchestration is in real_job.py."""
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo
import json

import numpy as np

from app.models import DayRecord
from data import real_checks as rc
from data.fetch_real import AirNowAdapter, CimisAdapter, to_local_hourly
from data.fetcher import FetchError, Fetcher


def _coord(v) -> float:  # CIMIS lists e.g. "36º49'13N / 36.820083" (assumed); take the decimal part
    return float(str(v).split("/")[-1].strip())


def select_sources(fetcher: Fetcher, cfg: dict, region: str, center: dict, keys: dict, probe: date):
    """Nearest active CIMIS station with hourly data, and nearest AirNow PM2.5 monitor within airnow_max_km."""
    rd, job, tz = cfg["real_data"], cfg["real_job"], ZoneInfo(cfg["real_data"]["local_tz"])
    stations = fetcher.get(job["cimis_station_list_url"], {}, "cimis/stations").get("Stations", [])
    cands = []
    for s in stations:
        try:
            if str(s.get("IsActive")).lower() == "true":
                km = rc.haversine_km(center["lat"], center["lon"], _coord(s["HmsLatitude"]), _coord(s["HmsLongitude"]))
                cands.append((km, str(s["StationNbr"]), s.get("Name", "")))
        except (KeyError, ValueError):
            continue
    cimis, cimis_probe = None, None
    for km, nbr, name in sorted(cands)[:job["cimis_max_candidates"]]:
        ad = CimisAdapter({**rd["cimis"], "station": nbr}, tz)
        payload = fetcher.get(rd["cimis"]["url"], ad.params(probe, keys["CIMIS_APPKEY"]), f"cimis/{nbr}/{probe}")
        if any(ad.parse(payload)["temp_f"]):
            cimis, cimis_probe = {"station": nbr, "name": name, "distance_km": round(km, 1)}, payload
            break
    if cimis is None:
        return None, "no active CIMIS station with hourly data among the nearest candidates", None, None
    d, c = job["airnow_search_deg"], center
    ad = AirNowAdapter({**rd["airnow"], "bbox": f"{c['lon'] - d},{c['lat'] - d},{c['lon'] + d},{c['lat'] + d}"}, tz)
    payload = fetcher.get(rd["airnow"]["url"], {**ad.params(probe, keys["AIRNOW_KEY"]), "verbose": 1},
                          f"airnow/search-{region}/{probe}")
    sites = {}
    for r in payload if isinstance(payload, list) else []:
        if "IntlAQSCode" in r and "Latitude" in r and "Longitude" in r:
            sites[str(r["IntlAQSCode"])] = (rc.haversine_km(c["lat"], c["lon"], r["Latitude"], r["Longitude"]), r)
    near = sorted((km, code, r) for code, (km, r) in sites.items() if km <= job["airnow_max_km"])
    if not near:
        return None, f"no AirNow PM2.5 monitor within {job['airnow_max_km']} km", cimis_probe, payload
    km, code, r = near[0]
    b = job["airnow_site_box_deg"]
    airnow = {"site": code, "name": r.get("SiteName", ""), "distance_km": round(km, 1),
              "bbox": f"{r['Longitude'] - b},{r['Latitude'] - b},{r['Longitude'] + b},{r['Latitude'] + b}"}
    return {"cimis": cimis, "airnow": airnow}, None, cimis_probe, payload


def build_day(fetcher: Fetcher, cfg: dict, region: str, src: dict, day: date, keys: dict):
    rd, tz = cfg["real_data"], ZoneInfo(cfg["real_data"]["local_tz"])
    cim = CimisAdapter({**rd["cimis"], "station": src["cimis"]["station"]}, tz)
    air = AirNowAdapter({**rd["airnow"], "bbox": src["airnow"]["bbox"]}, tz)
    cp = fetcher.get(rd["cimis"]["url"], cim.params(day, keys["CIMIS_APPKEY"]), f"cimis/{src['cimis']['station']}/{day}")
    ap = fetcher.get(rd["airnow"]["url"], {**air.params(day, keys["AIRNOW_KEY"]), "verbose": 1},
                     f"airnow/{src['airnow']['site']}/{day}")
    ap = [r for r in ap if str(r.get("IntlAQSCode", src["airnow"]["site"])) == src["airnow"]["site"]]
    hourly = {f: to_local_hourly(p, day, tz) for f, p in {**cim.parse(cp), **air.parse(ap)}.items()}
    filled, reasons, info = rc.assess_day(hourly, cfg["real_job"])
    if filled is None:
        return None, reasons, info
    meta = {"sources": {"temp_rh_solar": f"CIMIS station {src['cimis']['station']} {src['cimis']['name']}",
                        "pm25": f"AirNow {src['airnow']['site']} {src['airnow']['name']}"},
            "pm25_monitor_distance_km": src["airnow"]["distance_km"], **info}
    rec = DayRecord(id=f"real-{day.isoformat()}-{region}", region=region, provenance="real_cached", date=day.isoformat(),
                    meta=meta,
                    label=f"CIMIS {src['cimis']['name']} + AirNow {src['airnow']['name']} observed {day} ({region})",
                    **{f: np.round(np.repeat(v, 4), 3).tolist() for f, v in filled.items()})
    return rec, [], info


def run(cfg: dict, fetcher: Fetcher, cache_dir: Path, keys: dict):
    """Fetch and cache days. Returns (manifest, checks, stop_message or None)."""
    job, days = cfg["real_job"], rc.season_days(cfg["real_job"])
    manifest, checks, written = {"path": "cimis_airnow", "sources": {}, "excluded": []}, None, 0
    for region, center in job["regions"].items():
        try:
            src, why, cprobe, aprobe = select_sources(fetcher, cfg, region, center, keys, days[0])
        except (FetchError, KeyError, ValueError, TypeError, AttributeError) as e:
            src, why, cprobe, aprobe = None, f"source selection failed: {e}", None, None
        if checks is None and cprobe is not None and aprobe is not None:
            ok, checks = rc.preflight(cprobe, aprobe, cfg)
            if not ok:
                msg = "AirNow returned AQI only (no PM2.5 concentrations). Not converted; eval not run."
                return manifest, checks, msg
        if src is None:
            manifest["excluded"].append({"region": region, "reason": why})
            continue
        manifest["sources"][region] = src
        for day in rc.pending(days, region, cache_dir):
            try:
                rec, reasons, info = build_day(fetcher, cfg, region, src, day, keys)
            except (FetchError, KeyError, ValueError, TypeError) as e:
                rec, reasons, info = None, [f"fetch/parse error: {e}"], {}
            if rec is None:
                manifest["excluded"].append({"region": region, "date": day.isoformat(), "reasons": reasons, **info})
                continue
            (cache_dir / f"{rec.id}.json").write_text(json.dumps(rec.model_dump()), encoding="utf-8")
            written += 1
    manifest["written"] = written
    return manifest, checks or [], None
