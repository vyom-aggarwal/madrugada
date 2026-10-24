"""Keyless sources, NowCast, preregistration and source priority. Canned data only; network calls fail."""
import io
import zipfile
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from app.aqi import nowcast_aqi, nowcast_pm25
from app.config import load_config
from data import keyless as kl
from data import keyless_job, real_job
from data.fetch_real import ZoneInfo, to_local_hourly
from eval import prereg, run_eval

CFG = load_config()
COLS = CFG["keyless"]["airdata"]["columns"]
LA = ZoneInfo("America/Los_Angeles")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    import requests

    def boom(*a, **k):
        raise AssertionError("network call in tests")
    monkeypatch.setattr(requests, "get", boom)


IEM_CSV = "station,valid,lon,lat,tmpf,relh\n" + "".join(
    f"FAT,2024-07-01 {h:02d}:53,-119.7194,36.7800,{70 + h},{50 - h}\n" for h in range(24) if h not in (5, 6, 12, 13, 14))


def test_iem_parse_and_two_hour_interpolation():
    obs = kl.parse_iem_csv(IEM_CSV + "FAT,2024-07-01 20:10,-119.7,36.78,M,40\n", CFG["keyless"]["iem"]["fields"])
    assert obs[0]["valid"] == datetime(2024, 7, 1, 0, 53) and obs[0]["temp_f"] == 70.0
    assert np.isnan(obs[-1]["temp_f"]) and obs[-1]["rh"] == 40.0  # 'M' -> NaN, RH kept
    s = kl.asos_slots(obs, date(2024, 7, 1), 2)
    t = s["temp_f"]
    assert len(t) == 96
    # 04:53 -> 07:53 is a 3 h gap (05, 06 missing): rejected. Slot 06:00-06:15 midpoint 06:07.5 -> NaN.
    assert np.isnan(t[24]) and np.isnan(t[28])
    # 11:53 -> 15:53 is 4 h: rejected; 07:53 -> 08:53 is 1 h: interpolated linearly at 08:07.5.
    assert np.isnan(t[13 * 4]) and t[32] == pytest.approx(77 + (8 * 60 + 7.5 - (7 * 60 + 53)) / 60)
    two_gap = kl.parse_iem_csv("station,valid,lon,lat,tmpf,relh\nFAT,2024-07-01 10:00,0,0,80,10\n"
                               "FAT,2024-07-01 12:00,0,0,90,10\n", CFG["keyless"]["iem"]["fields"])
    t2 = kl.asos_slots(two_gap, date(2024, 7, 1), 2)["temp_f"]
    assert t2[40] == pytest.approx(80 + 10 * (7.5 / 120)) and np.isnan(t2[39])  # 2 h gap ok; before first: NaN
    assert t2[44] == pytest.approx(80 + 10 * (67.5 / 120))                        # 11:07.5


def _airdata_frame(rows):
    df = pd.DataFrame(rows, columns=list(COLS.values())).astype(str)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("hourly.csv", df.to_csv(index=False))
    buf.seek(0)
    return buf


def _row(state, county, site, poc, lat, lon, dl, tl, value, param="88101", units="Micrograms/cubic meter (LC)"):
    loc = datetime.strptime(f"{dl} {tl}", "%Y-%m-%d %H:%M")
    gmt = loc + timedelta(hours=8)
    return [state, county, site, poc, lat, lon, dl, tl, gmt.strftime("%Y-%m-%d"), gmt.strftime("%H:%M"), value, units, param]


def test_airdata_parse_filters_state_and_parameter_and_checks_standard_time():
    rows = [_row("06", "019", "0011", "3", 36.78, -119.77, "2024-07-01", "13:00", "12.5"),
            _row("6", "19", "11", "3", 36.78, -119.77, "2024-07-01", "14:00", "-2.0"),
            _row("32", "003", "0540", "1", 36.1, -115.1, "2024-07-01", "13:00", "9.0"),           # Nevada
            _row("06", "019", "0011", "3", 36.78, -119.77, "2024-07-01", "13:00", "40", "44201")]  # ozone
    df = kl.read_airdata(_airdata_frame(rows), COLS, "06", "88101")
    assert len(df) == 2 and set(df["_sid"]) == {"06-019-0011"}
    assert kl.local_minus_gmt_hours(df, COLS) == [-8.0]
    assert kl.monitor_series(df, COLS, "06-019-0011", "3") == {"2024-07-01": [(13, 12.5), (14, -2.0)]}


def test_nearest_monitor_selection_and_distance():
    rows = [_row("06", "019", "0011", p, 36.80, -119.75, "2024-07-01", "00:00", "5") for p in ("1", "3", "3")]
    rows += [_row("06", "019", "5001", "1", 36.70, -119.70, "2024-07-01", "00:00", "5"),
             _row("06", "029", "0014", "1", 35.40, -119.00, "2024-07-01", "00:00", "5")]   # ~150 km away
    df = kl.with_site_ids(pd.DataFrame(rows, columns=list(COLS.values())).astype(str), COLS)
    m = kl.nearest_monitor(df, COLS, 36.78, -119.72, date(2024, 6, 1), date(2024, 9, 30), 25)
    assert m["site"] == "06-019-0011" and m["poc"] == "3" and m["n_hours"] == 2
    assert m["distance_km"] == pytest.approx(kl.haversine_km(36.78, -119.72, 36.80, -119.75), abs=0.01)
    assert kl.nearest_monitor(df, COLS, 34.0, -118.0, date(2024, 6, 1), date(2024, 9, 30), 25) is None


TRANSITIONS = {  # value = UTC hours since D 00:00Z of each LST reading; expected per local clock hour
    date(2025, 3, 9): lambda h: h + 8 if h < 2 else (9.5 if h == 2 else h + 7),
    date(2025, 11, 2): lambda h: 7 if h == 0 else (8.5 if h == 1 else h + 8),
    date(2025, 7, 15): lambda h: h + 7,
}


@pytest.mark.parametrize("day", list(TRANSITIONS))
def test_airdata_standard_time_to_local_clock(day):
    series = {}
    for k in range(-12, 40):  # UTC hour k -> LST = UTC - 8
        lst = datetime(day.year, day.month, day.day) + timedelta(hours=k - 8)
        series.setdefault(lst.date().isoformat(), []).append((lst.hour, float(k)))
    hourly = to_local_hourly(kl.airdata_points(series, day, -8), day, LA)
    filled = __import__("data.real_checks", fromlist=["x"]).fill_short_gaps(hourly, 2)
    assert [filled[h] for h in range(24)] == pytest.approx([TRANSITIONS[day](h) for h in range(24)])


def _keyless_inputs(missing_pm_hours=(), negatives=()):
    day = date(2024, 7, 1)
    obs = [{"valid": datetime(2024, 6, 30, 22, 53) + timedelta(hours=i), "temp_f": 80.0 + i % 10, "rh": 30.0,
            "lat": 36.78, "lon": -119.72} for i in range(30)]
    series = {}
    for k in range(-2, 26):  # LST hour k of July 1 (local PDT clock hour = k + 1)
        lst = datetime(2024, 7, 1) + timedelta(hours=k)
        if k + 1 in missing_pm_hours:
            continue
        series.setdefault(lst.date().isoformat(), []).append((lst.hour, -3.0 if k + 1 in negatives else 20.0))
    return day, obs, series


def test_keyless_day_usability_and_negative_flags():
    station, mon = {"icao": "KFAT"}, {"site": "06-019-0011", "poc": "3", "distance_km": 4.2}
    day, obs, series = _keyless_inputs(negatives=(9, 10))
    rec, reasons, info = keyless_job.build_day(day, "fresno", "Fresno", station, mon, obs, series, CFG)
    assert rec is not None and rec.provenance == "real_cached" and rec.solar_wm2 == [0.0] * 96
    assert rec.meta["invalid_input_hours"] == 2 and rec.pm25_ugm3[36] == 0.0  # clamped (local 09:00)
    assert "solar_unavailable" in rec.meta["warnings"] and rec.meta["pm25_monitor_distance_km"] == 4.2
    assert "EPA AirData 88101 site 06-019-0011 POC 3" in rec.meta["sources"]["pm25"]
    day, obs, series = _keyless_inputs(missing_pm_hours=(3, 4, 5))  # 3 h gap: not filled -> 87.5%
    rec, reasons, _ = keyless_job.build_day(day, "fresno", "Fresno", station, mon, obs, series, CFG)
    assert rec is None and "pm25_ugm3" in reasons[0] and "need 90%" in reasons[0]
    day, obs, series = _keyless_inputs(missing_pm_hours=(3, 4))  # 2 h gap: filled -> usable
    assert keyless_job.build_day(day, "fresno", "Fresno", station, mon, obs, series, CFG)[0] is not None


def test_nowcast_hand_computed():
    assert nowcast_pm25([10.0] * 12)[-1] == pytest.approx(10.0)                     # constant: w = 1
    assert nowcast_pm25([20.0, 10.0])[-1] == pytest.approx((10 + 0.5 * 20) / 1.5)    # w = 1 - 10/20 = 0.5
    big = nowcast_pm25([10.0] * 11 + [100.0])[-1]                                    # w = 0.1 -> floor 0.5
    assert big == pytest.approx((100 + 10 * (1 - 0.5 ** 11)) / (2 - 0.5 ** 11))
    assert np.isnan(nowcast_pm25([10.0, 10.0, 10.0, np.nan, np.nan])[-1])           # < 2 of 3 recent valid
    assert nowcast_aqi([10.0] * 12)[-1] == 53 and np.isnan(nowcast_aqi([np.nan] * 3)[-1])


def test_preregistration_hash_check(tmp_path):
    good = tmp_path / "PREREGISTRATION.md"
    good.write_text(prereg.render("2026-10-24"), encoding="utf-8")
    assert prereg.verify(good) == (True, [])
    bad = tmp_path / "bad.md"
    bad.write_text(good.read_text(encoding="utf-8").replace(prereg.current_hashes()["app/optimizer.py"], "0" * 64),
                   encoding="utf-8")
    ok, problems = prereg.verify(bad)
    assert not ok and problems == ["app/optimizer.py: hash differs"]
    assert "eval/report.py" not in prereg.current_hashes()  # documented non-logic file
    cfg = load_config()
    changed = {**cfg, "keyless": {**cfg["keyless"], "iem": {**cfg["keyless"]["iem"], "url": "https://x.invalid"}}}
    assert prereg.config_logic_hash(changed) == prereg.config_logic_hash(cfg)  # URL is non-logic
    weights = {**cfg, "weights": {**cfg["weights"], "w_dual": 9}}
    assert prereg.config_logic_hash(weights) != prereg.config_logic_hash(cfg)


def test_eval_refuses_real_days_without_matching_preregistration(tmp_path, test_days, history):
    src = history + test_days
    real = [d.model_copy(update={"id": f"real-x-{i}", "region": "testreal", "provenance": "real_cached",
                                 "date": (date(2024, 6, 1) + timedelta(days=i)).isoformat()})
            for i, d in enumerate(src + src[:10])]  # 30 consecutive days -> 23 evaluable
    with pytest.raises(run_eval.PreregistrationError, match="refusing"):
        run_eval.run(pool=real, prereg_path=tmp_path / "missing.md")
    res = run_eval.run(pool=real[:20], prereg_path=tmp_path / "missing.md")  # 13 evaluable < 20: no check
    assert res["n_days"]["real_cached"] == 0 and "insufficient real days" in res["real_status"]


def test_source_priority():
    assert real_job.choose_path({"CIMIS_APPKEY": "a", "AIRNOW_KEY": "b"}) == "cimis_airnow"
    assert real_job.choose_path({"CIMIS_APPKEY": "a"}) == "keyless"
    assert real_job.choose_path({}) == "keyless"
