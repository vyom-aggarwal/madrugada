"""Real-data job (python tasks.py real): CIMIS + AirNow for the configured regions and seasons.

Raw responses are cached under data/cache/raw/ (resume without re-downloading), DayRecords go to
data/cache/<id>.json (provenance="real_cached"), station choices and excluded days go to
data/cache/meta/manifest.json, and API convention checks go to docs/real_data_notes.md. If AirNow
returns only AQI (no concentrations), the job stops before caching days or running the eval.
"""
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import load_config  # noqa: E402
from app.models import DayRecord  # noqa: E402
from data import real_checks as rc  # noqa: E402
from data.fetch_real import AirNowAdapter, CimisAdapter, to_local_hourly  # noqa: E402

CACHE = ROOT / "data" / "cache"
NOTES = ROOT / "docs" / "real_data_notes.md"
KEYS = ("CIMIS_APPKEY", "AIRNOW_KEY")


class FetchError(RuntimeError):
    pass


class Fetcher:
    """GET JSON with a raw-response cache (resume), a minimum interval between calls, and exponential
    backoff on 429/5xx/network errors. Error messages never include request parameters (API keys)."""

    def __init__(self, raw_dir: Path, throttle: dict, sleep=time.sleep, clock=time.monotonic):
        self.raw_dir, self.t, self.sleep, self.clock, self.last = raw_dir, throttle, sleep, clock, -1e9
        self.network_calls = 0

    def get(self, url: str, params: dict, cache_key: str):
        path = self.raw_dir / f"{cache_key}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        import requests
        for attempt in range(self.t["max_retries"] + 1):
            wait = self.t["min_interval_s"] - (self.clock() - self.last)
            if wait > 0:
                self.sleep(wait)
            self.last = self.clock()
            self.network_calls += 1
            try:
                r = requests.get(url, params=params, timeout=60, headers={"Accept": "application/json"})
                retry, err = r.status_code == 429 or r.status_code >= 500, f"HTTP {r.status_code}"
                if 400 <= r.status_code < 500 and not retry:
                    raise FetchError(f"{cache_key}: {err} (not retried)")
                if not retry:
                    data = r.json()
                    break
            except requests.RequestException as e:
                retry, err = True, e.__class__.__name__
            if attempt == self.t["max_retries"]:
                raise FetchError(f"{cache_key}: {err} after {attempt + 1} attempts")
            self.sleep(self.t["backoff_base_s"] * 2 ** attempt)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return data


def season_days(job: dict) -> list[date]:
    out = []
    for y in job["years"]:
        start = date.fromisoformat(f"{y}-{job['season']['start']}") - timedelta(days=job["history_days_before_start"])
        end = date.fromisoformat(f"{y}-{job['season']['end']}")
        out += [start + timedelta(days=i) for i in range((end - start).days + 1)]
    return out


def pending(days: list[date], region: str, cache_dir: Path = CACHE) -> list[date]:
    """Days without a cached DayRecord yet (resume)."""
    return [d for d in days if not (cache_dir / f"real-{d.isoformat()}-{region}.json").exists()]


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
    rec = DayRecord(id=f"real-{day.isoformat()}-{region}", region=region, provenance="real_cached", date=day.isoformat(),
                    label=f"CIMIS {src['cimis']['name']} + AirNow {src['airnow']['name']} observed {day} ({region})",
                    **{f: np.round(np.repeat(v, 4), 3).tolist() for f, v in filled.items()})
    return rec, [], info


def main() -> int:
    keys = {k: os.environ.get(k, "") for k in KEYS}
    if not all(keys.values()):
        print(f"real_job: missing API key env var(s): {', '.join(k for k, v in keys.items() if not v)}.")
        return 0
    cfg = load_config()
    job, days = cfg["real_job"], season_days(cfg["real_job"])
    fetcher = Fetcher(CACHE / "raw", job["throttle"])
    manifest, checks, written = {"sources": {}, "excluded": []}, None, 0
    for region, center in job["regions"].items():
        try:
            src, why, cprobe, aprobe = select_sources(fetcher, cfg, region, center, keys, days[0])
        except (FetchError, KeyError, ValueError, TypeError, AttributeError) as e:
            src, why, cprobe, aprobe = None, f"source selection failed: {e}", None, None
        if checks is None and cprobe is not None and aprobe is not None:
            ok, checks = rc.preflight(cprobe, aprobe, cfg)
            if not ok:
                msg = "AirNow returned AQI only (no PM2.5 concentrations). Not converted; eval not run."
                NOTES.parent.mkdir(parents=True, exist_ok=True)
                NOTES.write_text(rc.notes_markdown(checks, {}, msg, []), encoding="utf-8")
                print(f"real_job STOPPED: {msg} See {NOTES}.")
                return 3
        if src is None:
            manifest["excluded"].append({"region": region, "reason": why})
            continue
        manifest["sources"][region] = src
        for day in pending(days, region):
            try:
                rec, reasons, info = build_day(fetcher, cfg, region, src, day, keys)
            except (FetchError, KeyError, ValueError, TypeError) as e:
                rec, reasons, info = None, [f"fetch/parse error: {e}"], {}
            if rec is None:
                manifest["excluded"].append({"region": region, "date": day.isoformat(), "reasons": reasons, **info})
                continue
            (CACHE / f"{rec.id}.json").write_text(json.dumps(rec.model_dump()), encoding="utf-8")
            written += 1
    n_real = len(list(CACHE.glob("real-*.json")))
    summary = [f"days written this run: {written}", f"real_cached days in cache: {n_real}",
               f"excluded (this run): {len(manifest['excluded'])}", f"network calls: {fetcher.network_calls}"]
    (CACHE / "meta").mkdir(parents=True, exist_ok=True)
    (CACHE / "meta" / "manifest.json").write_text(json.dumps({**manifest, "summary": summary}, indent=1), encoding="utf-8")
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text(rc.notes_markdown(checks or [], manifest["sources"], None, summary), encoding="utf-8")
    print("\n".join(summary))
    from app.snapshot import main as build_snapshot
    from eval.run_eval import run, write
    write(run())
    build_snapshot()
    return 0


if __name__ == "__main__":
    sys.exit(main())
