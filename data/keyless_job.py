"""Keyless real-data path: IEM ASOS temperature/RH + EPA AirData hourly PM2.5, cached as real_cached days.

Checks the live sources against config.yaml conventions on first use (returned as `checks`), excludes
years whose AirData file is missing or incomplete, and stops (no silent conversion) if AirData is not
reachable or is not concentrations, or if its Time Local convention differs from the assumption.
"""
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from app.aqi import pm25_to_aqi
from app.models import DayRecord
from data import keyless as kl
from data import real_checks as rc
from data.fetch_real import to_local_hourly
from data.fetcher import FetchError, Fetcher

C = rc._check


def build_day(day: date, region: str, label: str, station: dict, mon: dict, obs: list, series: dict, cfg: dict):
    k, job, tz = cfg["keyless"], cfg["real_job"], ZoneInfo(cfg["real_data"]["local_tz"])
    gap = k["iem"]["max_gap_hours"]
    sl = kl.asos_slots(kl.obs_window(obs, day, gap + 1), day, gap)
    pm_h = to_local_hourly(kl.airdata_points(series, day, k["airdata"]["time_local_utc_offset_hours"]), day, tz)
    fin = ~np.isnan(pm_h)
    negative = int(pm25_to_aqi(pm_h[fin]).invalid_input.sum()) if fin.any() else 0  # flagged via app/aqi.py
    pm = np.repeat(rc.fill_short_gaps(np.where(fin, np.maximum(pm_h, 0.0), np.nan), job["max_gap_hours"]), 4)
    frac = {"temp_f": float(np.mean(np.isfinite(sl["temp_f"]))), "pm25_ugm3": float(np.mean(np.isfinite(pm)))}
    info = {f"{f}_observed_fraction": round(v, 4) for f, v in frac.items()}
    reasons = [f"{f}: {v:.0%} of slots observed after filling gaps <= {gap} h (need {job['usable_fraction']:.0%})"
               for f, v in frac.items() if v < job["usable_fraction"]]
    if reasons:
        return None, reasons, info
    slots, warnings, filled = np.arange(96), ["solar_unavailable"], {}
    out = {}
    for f, v in (("temp_f", sl["temp_f"]), ("pm25_ugm3", pm), ("rh", sl["rh"])):
        ok = np.isfinite(v)
        filled[f] = int((~ok).sum())
        out[f] = np.interp(slots, slots[ok], v[ok]) if ok.any() else np.full(96, np.nan)
    if not np.isfinite(out["rh"]).any():
        warnings.append("rh_unavailable")
    if negative:
        warnings.append(f"invalid_input: {negative} negative PM2.5 hour(s) clamped to 0")
    meta = {"sources": {"temp_rh": f"IEM ASOS {station['icao']}", "pm25": f"EPA AirData 88101 site {mon['site']} "
                        f"POC {mon['poc']}", "solar": "unavailable (constant 0)"},
            "pm25_monitor_distance_km": mon["distance_km"], "invalid_input_hours": negative,
            "slots_filled_beyond_rule": filled, "warnings": warnings, **info}
    rec = DayRecord(id=f"real-{day.isoformat()}-{region}", region=region, provenance="real_cached", date=day.isoformat(),
                    label=f"IEM ASOS {station['icao']} + AirData {mon['site']} observed {day} ({label})",
                    temp_f=np.round(out["temp_f"], 2).tolist(), rh=np.round(out["rh"], 2).tolist(),
                    solar_wm2=[0.0] * 96, pm25_ugm3=np.round(out["pm25_ugm3"], 2).tolist(), meta=meta)
    return rec, [], info


def _airdata_year(fetcher: Fetcher, cfg: dict, year: int, listing: str) -> tuple[pd.DataFrame | None, list, str | None]:
    """(CA rows or None, checks, exclusion reason)."""
    a = cfg["keyless"]["airdata"]
    cols, raw = a["columns"], fetcher.raw_dir / "airdata"
    try:
        zp = fetcher.download(a["url_template"].format(year=year), f"airdata/hourly_{a['parameter_code']}_{year}", ".zip")
    except FetchError as e:
        return None, [C("AirData", f"{year} file reachable", "differed", str(e))], f"AirData {year} not reachable"
    ca = raw / f"ca_{a['parameter_code']}_{year}.csv"
    if ca.exists():
        df = kl.with_site_ids(pd.read_csv(ca, dtype=str), cols)
    else:
        df = kl.read_airdata(zp, cols, a["state_code"], a["parameter_code"])
        df.drop(columns="_sid").to_csv(ca, index=False)
    checks = [C("AirData", f"{year} file reachable and parsed", "confirmed", f"{len(df)} California rows")]
    units = sorted(df[cols["units"]].dropna().unique())
    conc = bool(units) and all(a["expected_units"].lower() in u.lower() for u in units)
    checks.append(C("AirData", f"{year} values are concentrations (ug/m3)", "confirmed" if conc else "differed", str(units)))
    summer = df[df[cols["date_local"]].str[5:7] == "07"]
    offs = kl.local_minus_gmt_hours(summer if len(summer) else df, cols)
    std = offs == [float(a["time_local_utc_offset_hours"])]
    checks.append(C("AirData", f"{year} Time Local is local STANDARD time (Local - GMT in July)",
                    "confirmed" if std else "differed", f"offsets {offs}"))
    m = re.search(rf"hourly_{a['parameter_code']}_{year}\.zip</a><BR>([\d,]+) Rows<BR>[\d,]+ KB<BR>As of ([\d-]+)", listing)
    checks.append(C("AirData", f"{year} data release status", "unverifiable",
                    f"listing: {m.group(1)} rows, as of {m.group(2)}; no preliminary/certified flag shown" if m
                    else "file not found on the listing page"))
    last = df[cols["date_local"]].max() if len(df) else ""
    end = f"{year}-{cfg['real_job']['season']['end']}"
    if not conc:
        return None, checks, "STOP: not concentrations"
    if not std:
        return None, checks, "STOP: Time Local convention differs"
    if last < end:
        return None, checks, f"AirData {year} incomplete for the window (last Date Local {last})"
    return df, checks, None


def _iem_checks(fetcher: Fetcher, cfg: dict, station: str, rows: list, header: str) -> list:
    i = cfg["keyless"]["iem"]
    names = set(header.strip().split(","))
    checks = [C("IEM", "fields " + ", ".join(i["fields"].values()), "confirmed" if set(i["fields"].values()) <= names
                else "differed", f"header {sorted(names)}")]
    t = np.array([r["temp_f"] for r in rows if np.isfinite(r["temp_f"])])
    h = np.array([r["rh"] for r in rows if np.isfinite(r["rh"])])
    checks.append(C("IEM", "temperature in F (tmpf plausible range)", "confirmed" if len(t) and t.min() > -20 and
                    t.max() < 130 else "differed", f"range {t.min():.0f}..{t.max():.0f}" if len(t) else "no values"))
    checks.append(C("IEM", "RH in percent (0..100)", "confirmed" if len(h) and h.min() >= 0 and h.max() <= 100
                    else "differed", f"range {h.min():.0f}..{h.max():.0f}" if len(h) else "no values"))
    probe = date(cfg["real_job"]["years"][0], 7, 1)
    loc = kl.parse_iem_csv(fetcher.get_text(i["url"], kl.iem_params(station, probe, probe + timedelta(days=2), i["tz"]),
                                            f"iem/{station}-probe-local", ".csv"), i["fields"])
    utc = kl.parse_iem_csv(fetcher.get_text(i["url"], kl.iem_params(station, probe, probe + timedelta(days=3), "Etc/UTC"),
                                            f"iem/{station}-probe-utc", ".csv"), i["fields"])
    by_utc = {r["valid"]: r["temp_f"] for r in utc}
    tz = ZoneInfo(i["tz"])
    pairs = [(r["temp_f"], by_utc.get(r["valid"].replace(tzinfo=tz).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)))
             for r in loc if np.isfinite(r["temp_f"])]
    match = [a == b for a, b in pairs if b is not None]
    ok = bool(match) and np.mean(match) >= 0.95
    checks.append(C("IEM", f"tz={i['tz']} returns local clock time (vs tz=Etc/UTC)", "confirmed" if ok else "differed",
                    f"{sum(match)} of {len(match)} matched reports equal after converting local -> UTC"))
    return checks


def run(cfg: dict, fetcher: Fetcher, cache_dir: Path):
    """Fetch and cache keyless days. Returns (manifest, checks, stop_message or None)."""
    k, job = cfg["keyless"], cfg["real_job"]
    manifest = {"path": "keyless (IEM ASOS + EPA AirData)", "sources": {}, "excluded": [], "years": {}, "written": 0}
    try:
        listing = fetcher.get_text(k["airdata"]["listing_url"], {}, "airdata/listing", ".html")
    except FetchError as e:
        listing = ""
        manifest["years"]["listing"] = f"unreachable: {e}"
    checks, frames = [], {}
    for y in job["years"]:
        df, ch, why = _airdata_year(fetcher, cfg, y, listing)
        checks += ch
        if why and why.startswith("STOP"):
            return manifest, checks, f"AirData {y}: {why[6:]}. Nothing converted; eval not run."
        manifest["years"][str(y)] = why or "included"
        if df is not None:
            frames[y] = df
    if not frames:
        return manifest, checks, "No AirData year is reachable and complete. Eval not run."
    for region, r in k["regions"].items():
        i = k["iem"]
        rows, header = [], ""
        for y in job["years"]:
            start = date.fromisoformat(f"{y}-{job['season']['start']}") - timedelta(days=job["history_days_before_start"] + 1)
            end = date.fromisoformat(f"{y}-{job['season']['end']}") + timedelta(days=2)
            text = fetcher.get_text(i["url"], kl.iem_params(r["asos"], start, end, i["tz"]), f"iem/{r['asos']}-{y}", ".csv")
            header = header or text.split("\n", 1)[0]
            rows += kl.parse_iem_csv(text, i["fields"])
        if region == next(iter(k["regions"])):
            checks += _iem_checks(fetcher, cfg, r["asos"], rows, header)
        lat = next((x["lat"] for x in rows if np.isfinite(x["lat"])), None)
        lon = next((x["lon"] for x in rows if np.isfinite(x["lon"])), None)
        station = {"icao": r["icao"], "lat": lat, "lon": lon}
        manifest["sources"][region] = {"asos": station, "monitors": {}}
        for y, df in frames.items():
            days = rc.season_days(job, y)
            mon = kl.nearest_monitor(df, k["airdata"]["columns"], lat, lon, days[0], days[-1], k["airdata"]["max_km"])
            if mon is None:
                manifest["excluded"].append({"region": region, "year": y, "reason": f"no active PM2.5 monitor within "
                                                                                    f"{k['airdata']['max_km']} km"})
                continue
            manifest["sources"][region]["monitors"][str(y)] = mon
            series = kl.monitor_series(df, k["airdata"]["columns"], mon["site"], mon["poc"])
            for day in rc.pending(days, region, cache_dir):
                rec, reasons, info = build_day(day, region, r["label"], station, mon, rows, series, cfg)
                if rec is None:
                    manifest["excluded"].append({"region": region, "date": day.isoformat(), "reasons": reasons, **info})
                    continue
                (cache_dir / f"{rec.id}.json").write_text(json.dumps(rec.model_dump()), encoding="utf-8")
                manifest["written"] += 1
    return manifest, checks, None
