"""Pure helpers for the real-data job: short-gap filling, the usability rule, live-API schema checks.

No network here; everything is testable with canned data.
"""
import math
import re

import numpy as np

USABILITY_FIELDS = ("temp_f", "pm25_ugm3")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2, dp, dl = map(math.radians, (lat1, lat2, lat2 - lat1, lon2 - lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def fill_short_gaps(hourly, max_gap_hours: int) -> np.ndarray:
    """Linearly interpolate interior NaN runs of at most max_gap_hours. Longer runs and runs touching
    the start or end of the day stay NaN."""
    v = np.asarray(hourly, dtype=float).copy()
    i, n = 0, len(v)
    while i < n:
        if not np.isnan(v[i]):
            i += 1
            continue
        j = i
        while j < n and np.isnan(v[j]):
            j += 1
        if i > 0 and j < n and j - i <= max_gap_hours:
            v[i:j] = np.interp(np.arange(i, j), [i - 1, j], [v[i - 1], v[j]])
        i = j
    return v


def assess_day(hourly: dict[str, np.ndarray], job: dict) -> tuple[dict | None, list[str], dict]:
    """Usability rule: temp and PM2.5 each need >= usable_fraction of slots observed after filling gaps of
    up to max_gap_hours. Returns (24-hour arrays with remaining edge gaps held at the nearest value, or None
    if unusable; reasons; info such as observed fractions and how many hours were edge-filled)."""
    filled, reasons, info = {}, [], {}
    for f, v in hourly.items():
        g = fill_short_gaps(v, job["max_gap_hours"])
        frac = float(np.mean(~np.isnan(g)))
        info[f"{f}_observed_fraction"] = round(frac, 4)
        if np.isnan(g).all():
            reasons.append(f"{f}: no data")
        elif f in USABILITY_FIELDS and frac < job["usable_fraction"]:
            reasons.append(f"{f}: {frac:.0%} of slots observed after filling gaps <= {job['max_gap_hours']} h "
                           f"(need {job['usable_fraction']:.0%})")
        filled[f] = g
    missing = [f for f in USABILITY_FIELDS if f not in hourly]
    reasons += [f"{f}: not returned" for f in missing]
    if reasons:
        return None, reasons, info
    hours = np.arange(24)
    for f, g in filled.items():
        ok = ~np.isnan(g)
        info[f"{f}_hours_filled_beyond_rule"] = int((~ok).sum())  # edge gaps (or rh/solar gaps): nearest/linear
        filled[f] = np.interp(hours, hours[ok], g[ok])
    return filled, [], info


def _check(source: str, item: str, status: str, detail: str) -> dict:
    return {"source": source, "item": item, "status": status, "detail": detail}


def check_cimis(payload, cimis_cfg: dict, expected_units: dict) -> list[dict]:
    """Compare a live CIMIS hourly response to the conventions assumed in config.yaml."""
    try:
        recs = payload["Data"]["Providers"][0]["Records"]
    except (KeyError, IndexError, TypeError):
        return [_check("CIMIS", "structure Data.Providers[0].Records", "differed", "not found")]
    out = [_check("CIMIS", "structure Data.Providers[0].Records", "confirmed" if recs else "differed",
                  f"{len(recs)} records")]
    if not recs:
        return out
    r = recs[0]
    for f, name in cimis_cfg["response_fields"].items():
        present = isinstance(r.get(name), dict) and "Value" in r[name]
        out.append(_check("CIMIS", f"field {name}.Value ({f})", "confirmed" if present else "differed",
                          "present" if present else f"absent; record keys: {sorted(r)[:15]}"))
        unit = str((r.get(name) or {}).get("Unit", ""))
        exp = expected_units.get(f, "")
        out.append(_check("CIMIS", f"unit of {name}", "confirmed" if exp.lower() in unit.lower() else "differed",
                          f"got {unit!r}, expected to contain {exp!r}"))
    ok_date = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("Date", ""))))
    out.append(_check("CIMIS", "Date is YYYY-MM-DD", "confirmed" if ok_date else "differed", repr(r.get("Date"))))
    hours = sorted({str(x.get("Hour", "")) for x in recs})
    ok_hours = all(h.isdigit() and len(h) == 4 and h.endswith("00") and 100 <= int(h) <= 2400 for h in hours)
    out.append(_check("CIMIS", "Hour is hour-ending HH00 (0100..2400)", "confirmed" if ok_hours else "differed",
                      f"values {hours[:2]} .. {hours[-2:]}"))
    if "Standard" in r:
        std = str(r["Standard"]).lower()
        out.append(_check("CIMIS", "timezone: Pacific Standard Time year-round",
                          "confirmed" if std == "pst" else "differed", f"Standard={r['Standard']!r}"))
    else:
        out.append(_check("CIMIS", "timezone: Pacific Standard Time year-round", "unverifiable",
                          "no timezone field in the record; assumption kept"))
    return out


def airnow_concentrations_available(payload) -> bool:
    """True if records carry PM2.5 concentrations in ug/m3 (not only AQI)."""
    recs = [r for r in payload or [] if isinstance(r, dict)]
    return any(isinstance(r.get("Value"), (int, float)) and "UG/M3" in str(r.get("Unit", "")).upper() for r in recs)


def check_airnow(payload) -> list[dict]:
    recs = [r for r in payload or [] if isinstance(r, dict)] if isinstance(payload, list) else []
    out = [_check("AirNow", "response is a list of records", "confirmed" if recs else "differed",
                  f"{len(recs)} records")]
    if not recs:
        return out
    r = recs[0]
    if "UTC" in r:
        out.append(_check("AirNow", "time convention", "confirmed", "'UTC' field present: treated as UTC hour-beginning"))
    elif {"DateObserved", "HourObserved", "LocalTimeZone"} <= set(r):
        out.append(_check("AirNow", "time convention", "confirmed", "local DateObserved/HourObserved/LocalTimeZone"))
    else:
        out.append(_check("AirNow", "time convention", "differed", f"no UTC or local time fields; keys {sorted(r)}"))
    params = {str(x.get("Parameter", "")) for x in recs}
    out.append(_check("AirNow", "Parameter is PM2.5", "confirmed" if params <= {"PM2.5"} else "differed", str(sorted(params))))
    conc = airnow_concentrations_available(recs)
    out.append(_check("AirNow", "returns PM2.5 concentrations (ug/m3), not only AQI",
                      "confirmed" if conc else "differed",
                      "Value with Unit UG/M3 present" if conc else f"no concentration values; keys {sorted(r)}"))
    site = all(k in r for k in ("IntlAQSCode", "Latitude", "Longitude"))
    out.append(_check("AirNow", "site fields IntlAQSCode/Latitude/Longitude (verbose)", "confirmed" if site else "differed",
                      "present" if site else f"keys {sorted(r)}"))
    return out


def preflight(cimis_payload, airnow_payload, cfg: dict) -> tuple[bool, list[dict]]:
    """Checks on the first live responses. ok=False means stop before caching or evaluating anything
    (currently: AirNow returns only AQI, which must not be converted silently)."""
    checks = check_cimis(cimis_payload, cfg["real_data"]["cimis"], cfg["real_job"]["cimis_expected_units"])
    checks += check_airnow(airnow_payload)
    return airnow_concentrations_available(airnow_payload), checks


def notes_markdown(checks: list[dict], sources: dict, stopped: str | None, summary: list[str]) -> str:
    lines = ["# Real-data API notes", "", "Generated by `python tasks.py real` (data/real_job.py) from the first live "
             "responses. Compares the APIs with the conventions assumed in config.yaml.", ""]
    if stopped:
        lines += [f"**STOPPED:** {stopped}", ""]
    for status in ("confirmed", "differed", "unverifiable"):
        rows = [c for c in checks if c["status"] == status]
        lines += [f"## {status.capitalize()} ({len(rows)})", ""] + [
            f"- {c['source']}: {c['item']} - {c['detail']}" for c in rows] + [""]
    lines += ["## Sources chosen per region", ""] + [f"- {r}: {s}" for r, s in sources.items()] + [""]
    lines += ["## Summary", ""] + [f"- {s}" for s in summary] + [""]
    return "\n".join(lines)
