"""Keyless real-data sources: IEM ASOS (temperature, RH) and EPA AirData hourly PM2.5 (parameter 88101).

Parsing and conversion are pure functions (testable with canned data); fetching lives in data/real_job.py.
URLs, field names, units and time conventions come from config.yaml `keyless` (unverified until checked).
"""
import csv
import io
from datetime import date, datetime, time, timedelta, timezone

import numpy as np
import pandas as pd

from data.real_checks import haversine_km


# ---------- IEM ASOS ----------
def iem_params(station: str, start: date, end_exclusive: date, tz: str) -> dict:
    return {"station": station, "data": ["tmpf", "relh"], "year1": start.year, "month1": start.month,
            "day1": start.day, "year2": end_exclusive.year, "month2": end_exclusive.month,
            "day2": end_exclusive.day, "tz": tz, "format": "onlycomma", "latlon": "yes", "missing": "M",
            "trace": "T", "direct": "no", "report_type": [3, 4]}


def _num(s) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return float("nan")


def parse_iem_csv(text: str, fields: dict) -> list[dict]:
    """Rows of {valid: naive local datetime, temp_f, rh, lat, lon}; 'M' (missing) becomes NaN."""
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            valid = datetime.strptime(row[fields["valid"]].strip(), "%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            continue
        out.append({"valid": valid, **{k: _num(row.get(fields[k])) for k in ("temp_f", "rh", "lat", "lon")}})
    return out


def asos_slots(obs: list[dict], day: date, max_gap_hours: float, n_slots: int = 96) -> dict[str, np.ndarray]:
    """Irregular reports (hourly + specials, naive local wall-clock) -> values at the midpoint of each
    15-minute local slot of `day`, by linear interpolation between the two neighbouring reports when they
    are at most max_gap_hours apart; otherwise NaN. (Interpolation is in wall-clock minutes; the June-Sept
    window has no DST transition.)"""
    t0 = datetime.combine(day, time(0))
    step = 24 * 60 / n_slots
    mids = np.arange(n_slots) * step + step / 2
    out = {}
    for f in ("temp_f", "rh"):
        pts = sorted(((o["valid"] - t0).total_seconds() / 60, o[f]) for o in obs if np.isfinite(o[f]))
        if not pts:
            out[f] = np.full(n_slots, np.nan)
            continue
        t, v = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
        hi = np.searchsorted(t, mids, side="left")
        lo = hi - 1
        inside = (lo >= 0) & (hi < len(t))
        lo_c, hi_c = np.clip(lo, 0, len(t) - 1), np.clip(hi, 0, len(t) - 1)
        gap = t[hi_c] - t[lo_c]
        w = (mids - t[lo_c]) / np.where(gap > 0, gap, 1)
        val = np.where(inside & (gap <= max_gap_hours * 60), v[lo_c] + w * (v[hi_c] - v[lo_c]), np.nan)
        exact = (hi < len(t)) & (t[hi_c] == mids)
        out[f] = np.where(exact, v[hi_c], val)
    return out


def obs_window(obs: list[dict], day: date, pad_hours: float) -> list[dict]:
    lo = datetime.combine(day, time(0)) - timedelta(hours=pad_hours)
    hi = datetime.combine(day + timedelta(days=1), time(0)) + timedelta(hours=pad_hours)
    return [o for o in obs if lo <= o["valid"] <= hi]


# ---------- EPA AirData ----------
def read_airdata(path_or_buffer, cols: dict, state_code: str, param: str, compression="zip") -> pd.DataFrame:
    """One state's rows of a national yearly hourly file (read in chunks; all columns as strings)."""
    parts = []
    for ch in pd.read_csv(path_or_buffer, compression=compression, usecols=list(cols.values()), dtype=str,
                          chunksize=500_000):
        keep = (ch[cols["state"]].str.zfill(2) == state_code) & (ch[cols["param"]] == param)
        if keep.any():
            parts.append(ch[keep])
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=list(cols.values()))
    return with_site_ids(df, cols)


def with_site_ids(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    """Add '_sid' = SS-CCC-NNNN (state-county-site), computed once, vectorized."""
    df = df.copy()
    df["_sid"] = (df[cols["state"]].astype(str).str.zfill(2) + "-" + df[cols["county"]].astype(str).str.zfill(3)
                  + "-" + df[cols["site"]].astype(str).str.zfill(4))
    return df


def nearest_monitor(df: pd.DataFrame, cols: dict, lat: float, lon: float, start: date, end: date,
                    max_km: float) -> dict | None:
    """Nearest site with data in [start, end] within max_km; at that site the POC with the most hourly
    values (ties: lowest POC). Returns {site, poc, lat, lon, distance_km, n_hours} or None."""
    d = df[(df[cols["date_local"]] >= start.isoformat()) & (df[cols["date_local"]] <= end.isoformat())]
    if d.empty:
        return None
    best = None
    for sid, g in d.groupby("_sid"):
        km = haversine_km(lat, lon, float(g[cols["lat"]].iloc[0]), float(g[cols["lon"]].iloc[0]))
        if km <= max_km and (best is None or km < best[0]):
            counts = g.groupby(cols["poc"]).size()
            poc = sorted(counts.index, key=lambda p: (-counts[p], int(p)))[0]
            best = (km, sid, str(poc), float(g[cols["lat"]].iloc[0]),
                    float(g[cols["lon"]].iloc[0]), int(counts[poc]))
    if best is None:
        return None
    return dict(zip(("distance_km", "site", "poc", "lat", "lon", "n_hours"), best)) | {"distance_km": round(best[0], 2)}


def monitor_series(df: pd.DataFrame, cols: dict, site: str, poc: str) -> dict[str, list[tuple[int, float]]]:
    """{Date Local: [(hour, value), ...]} for one site/POC."""
    sub = df[(df["_sid"] == site) & (df[cols["poc"]] == poc)]
    out: dict[str, list] = {}
    for dl, tl, v in zip(sub[cols["date_local"]], sub[cols["time_local"]], sub[cols["value"]]):
        out.setdefault(dl, []).append((int(str(tl)[:2]), _num(v)))
    return out


def airdata_points(series: dict, day: date, utc_offset_hours: float) -> list[tuple[datetime, float]]:
    """Aware interval-start points around `day`, reading Time Local as a fixed UTC offset (standard time)."""
    tz = timezone(timedelta(hours=utc_offset_hours))
    pts = []
    for d in (day - timedelta(days=1), day, day + timedelta(days=1)):
        for hour, v in series.get(d.isoformat(), []):
            if np.isfinite(v):
                pts.append((datetime.combine(d, time(hour), tz), v))
    return pts


def local_minus_gmt_hours(df: pd.DataFrame, cols: dict, n: int = 2000) -> list[float]:
    """Distinct (Local - GMT) offsets in hours over a sample of rows (verifies the Time Local convention)."""
    s = df.head(n)
    loc = pd.to_datetime(s[cols["date_local"]] + " " + s[cols["time_local"]])
    gmt = pd.to_datetime(s[cols["date_gmt"]] + " " + s[cols["time_gmt"]])
    return sorted({round(x / 3600, 2) for x in (loc - gmt).dt.total_seconds()})
