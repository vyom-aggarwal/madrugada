"""Source timestamps -> local clock slots (America/Los_Angeles), incl. DST transitions. No network.

Canned readings carry value k = hours since day D 00:00 UTC of the reading's interval start, so each
local slot's value tells us exactly which source hour landed there. Expected values below use
hand-written UTC offsets (PDT = -7, PST = -8), independent of zoneinfo.
"""
from datetime import date, datetime, timedelta, timezone

import pytest

from app.config import load_config
from data.fetch_real import AirNowAdapter, CimisAdapter, ZoneInfo, to_local_slots

CFG = load_config()["real_data"]
TZ = ZoneInfo(CFG["local_tz"])

CASES = {
    "summer": (date(2025, 7, 15), lambda h: h + 7),
    "winter": (date(2025, 1, 15), lambda h: h + 8),
    # 02:00 PST jumps to 03:00 PDT: clock hour 2 has no reading -> interpolated between 9 and 10.
    "spring_forward": (date(2025, 3, 9), lambda h: h + 8 if h < 2 else (9.5 if h == 2 else h + 7)),
    # 01:00 happens twice (PDT 08Z, then PST 09Z): averaged; 02:00 onward is PST.
    "fall_back": (date(2025, 11, 2), lambda h: 7 if h == 0 else (8.5 if h == 1 else h + 8)),
}


def _utc_hours(day):
    base = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return [(k, base + timedelta(hours=k)) for k in range(-12, 40)]


def _airnow_utc(day):
    return [{"UTC": t.strftime("%Y-%m-%dT%H:%M"), "Value": float(k)} for k, t in _utc_hours(day)]


def _airnow_local(day):
    out = []
    for k, t in _utc_hours(day):
        loc = t.astimezone(TZ)
        out.append({"DateObserved": loc.date().isoformat() + " ", "HourObserved": loc.hour,
                    "LocalTimeZone": loc.tzname(), "Value": float(k)})
    return out


def _cimis(day):
    recs = []
    for k, t in _utc_hours(day):
        pst = (t - timedelta(hours=8)).replace(tzinfo=None)  # hour-ending PST convention
        recs.append({"Date": pst.date().isoformat(), "Hour": f"{pst.hour + 1:02d}00",
                     "HlyRelHum": {"Value": str(k)}})
    return {"Data": {"Providers": [{"Records": recs}]}}


def _points(source, day):
    if source == "cimis":
        return CimisAdapter(CFG["cimis"], TZ).parse(_cimis(day))["rh"]
    payload = _airnow_utc(day) if source == "airnow_utc" else _airnow_local(day)
    return AirNowAdapter(CFG["airnow"], TZ).parse(payload)["pm25_ugm3"]


@pytest.mark.parametrize("source", ["cimis", "airnow_utc", "airnow_local"])
@pytest.mark.parametrize("case", list(CASES))
def test_local_clock_slots(source, case):
    day, expected = CASES[case]
    slots = to_local_slots(_points(source, day), day, TZ, CFG["max_missing_hours"], source)
    assert len(slots) == 96
    for i, v in enumerate(slots):
        assert v == pytest.approx(expected(i // 4)), f"{case} {source} slot {i} (clock hour {i // 4})"
    # No duplicated or dropped hours: each clock hour's value occupies exactly its 4 slots.
    hourly = [slots[4 * h] for h in range(24)]
    assert len(set(hourly)) == 24
    assert all(slots[4 * h: 4 * h + 4] == [hourly[h]] * 4 for h in range(24))
