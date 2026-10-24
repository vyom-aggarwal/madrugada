"""Fetch real observations (CIMIS weather + AirNow PM2.5) into data/cache/ as provenance="real_cached".

Usage: python data/fetch_real.py YYYY-MM-DD   (a LOCAL date in America/Los_Angeles)
Keys come from env vars CIMIS_APPKEY and AIRNOW_KEY; if either is missing, prints a message and exits 0.
Endpoints, parameter names, response fields, units and time conventions live in config.yaml
`real_data`, all UNVERIFIED. Output slots are local clock time (see to_local_slots).
"""
import json
import os
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import load_config  # noqa: E402
from app.models import SLOTS_PER_DAY, DayRecord  # noqa: E402

CACHE_DIR = ROOT / "data" / "cache"
Points = list[tuple[datetime, float]]  # (timezone-aware interval START, value)


class Adapter:
    """Common interface: fetch(day, key) -> {field: [(aware interval-start datetime, value), ...]}."""
    name = ""
    env_key = ""
    fields: tuple[str, ...] = ()

    def __init__(self, cfg: dict, tz: ZoneInfo):
        self.cfg, self.tz = cfg, tz

    def fetch(self, day: date, key: str) -> dict[str, Points]:
        return self.parse(self.request(day, key))

    def request(self, day: date, key: str):
        raise NotImplementedError

    def parse(self, payload) -> dict[str, Points]:
        raise NotImplementedError

    def _get(self, params: dict):
        import requests
        r = requests.get(self.cfg["url"], params=params, timeout=30,
                         headers={"Accept": "application/json"})
        r.raise_for_status()
        return r.json()


class CimisAdapter(Adapter):
    """Assumed (unverified): Date + Hour are hour-ENDING in a fixed offset (PST) year-round."""
    name, env_key, fields = "CIMIS", "CIMIS_APPKEY", ("temp_f", "rh", "solar_wm2")

    def request(self, day, key):
        c = self.cfg  # local day D spans PST dates D-1 (summer, 23:00 PST = 00:00 PDT) and D
        return self._get({"appKey": key, "targets": c["station"], "startDate": (day - timedelta(days=1)).isoformat(),
                          "endDate": day.isoformat(), "unitOfMeasure": c["units"],
                          "dataItems": ",".join(c["data_items"][f] for f in self.fields)})

    def parse(self, payload):
        src = timezone(timedelta(hours=self.cfg["source_utc_offset_hours"]))
        names = self.cfg["response_fields"]
        out: dict[str, Points] = {f: [] for f in self.fields}
        for rec in payload["Data"]["Providers"][0]["Records"]:
            hour_ending = int(rec["Hour"]) // 100  # "0100".."2400"
            start = datetime.combine(date.fromisoformat(rec["Date"]), time(0), src) + timedelta(hours=hour_ending - 1)
            for f in self.fields:
                v = (rec.get(names[f]) or {}).get("Value")
                if v in (None, ""):
                    continue
                v = float(v) * 9 / 5 + 32 if f == "temp_f" else float(v)  # metric request: C -> F
                out[f].append((start, v))
        return out


class AirNowAdapter(Adapter):
    """Assumed (unverified): hour-beginning; "UTC" field is UTC, else DateObserved/HourObserved/LocalTimeZone."""
    name, env_key, fields = "AirNow", "AIRNOW_KEY", ("pm25_ugm3",)

    def request(self, day, key):
        start = datetime.combine(day, time(0), self.tz).astimezone(timezone.utc)
        end = datetime.combine(day + timedelta(days=1), time(0), self.tz).astimezone(timezone.utc) - timedelta(hours=1)
        return self._get({"startDate": start.strftime("%Y-%m-%dT%H"), "endDate": end.strftime("%Y-%m-%dT%H"),
                          "parameters": "PM25", "BBOX": self.cfg["bbox"], "dataType": "C",
                          "format": "application/json", "API_KEY": key})

    def _start(self, rec) -> datetime:
        if "UTC" in rec:
            return datetime.strptime(rec["UTC"], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        off = self.cfg["local_tz_offsets"][rec["LocalTimeZone"].strip()]
        d = date.fromisoformat(rec["DateObserved"].strip())
        return datetime.combine(d, time(int(rec["HourObserved"])), timezone(timedelta(hours=off)))

    def parse(self, payload):
        pts = [(self._start(r), float(r["Value"])) for r in payload
               if r.get("Value") is not None and r["Value"] >= 0]  # negative = missing sentinel
        return {"pm25_ugm3": pts}


def to_local_hourly(points: Points, day: date, tz: ZoneInfo) -> np.ndarray:
    """24 wall-clock hourly means for local `day`. Each point lands on the local clock hour its interval
    starts in. Fall-back day: the repeated hour's two readings are averaged. Spring-forward day: the
    skipped hour has no reading (NaN)."""
    sums, counts = np.zeros(24), np.zeros(24)
    for t, v in points:
        if t.tzinfo is None:
            raise ValueError("source timestamps must be timezone-aware")
        local = t.astimezone(tz)
        if local.date() == day:
            sums[local.hour] += v
            counts[local.hour] += 1
    return np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)


def hourly_to_slots(values: np.ndarray, max_missing: int, field: str) -> list[float]:
    """Interpolate up to max_missing missing hours, then repeat each hour across its slots."""
    ok = ~np.isnan(values)
    if (~ok).sum() > max_missing:
        raise ValueError(f"{field}: {(~ok).sum()} of 24 hours missing (max {max_missing})")
    hours = np.arange(24)
    filled = np.interp(hours, hours[ok], values[ok])
    return np.round(np.repeat(filled, SLOTS_PER_DAY // 24), 3).tolist()


def to_local_slots(points: Points, day: date, tz: ZoneInfo, max_missing: int, field: str) -> list[float]:
    """Map source points to exactly SLOTS_PER_DAY local-clock slots for `day` (slot i = clock hour i // 4)."""
    return hourly_to_slots(to_local_hourly(points, day, tz), max_missing, field)


def build_day(day: date, adapters: list[Adapter], keys: dict[str, str], cfg: dict) -> DayRecord:
    tz = ZoneInfo(cfg["local_tz"])
    fields = {}
    for a in adapters:
        for f, pts in a.fetch(day, keys[a.env_key]).items():
            fields[f] = to_local_slots(pts, day, tz, cfg["max_missing_hours"], f)
    sources = "+".join(a.name for a in adapters)
    return DayRecord(id=f"real-{day.isoformat()}-{cfg['region']}", label=f"{sources} observed {day.isoformat()}",
                     region=cfg["region"], provenance="real_cached", date=day.isoformat(), **fields)


def make_adapters(cfg: dict) -> list[Adapter]:
    tz = ZoneInfo(cfg["local_tz"])
    return [CimisAdapter(cfg["cimis"], tz), AirNowAdapter(cfg["airnow"], tz)]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cfg = load_config()["real_data"]
    adapters = make_adapters(cfg)
    missing = [a.env_key for a in adapters if not os.environ.get(a.env_key)]
    if missing:
        print(f"fetch_real: missing API key env var(s): {', '.join(missing)}. Nothing fetched. "
              "Set them and re-run to cache real data.")
        return 0
    if len(argv) != 1:
        print("usage: python data/fetch_real.py YYYY-MM-DD")
        return 2
    rec = build_day(date.fromisoformat(argv[0]), adapters, {a.env_key: os.environ[a.env_key] for a in adapters}, cfg)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{rec.id}.json"
    path.write_text(json.dumps(rec.model_dump()), encoding="utf-8")
    print(f"wrote {path} (provenance=real_cached)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
