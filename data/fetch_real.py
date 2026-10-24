"""Fetch real observations (CIMIS weather + AirNow PM2.5) into data/cache/ as provenance="real_cached".

Usage: python data/fetch_real.py YYYY-MM-DD
Keys come from env vars CIMIS_APPKEY and AIRNOW_KEY; if either is missing, prints a message and exits 0.
Endpoints, parameter names, response fields and units live in config.yaml `real_data`, all UNVERIFIED.
"""
import json
import os
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config import load_config  # noqa: E402
from app.models import SLOTS_PER_DAY, DayRecord  # noqa: E402

CACHE_DIR = ROOT / "data" / "cache"


class Adapter:
    """Common interface: fetch(day, key) -> {field: 24 hourly local values, NaN where missing}."""
    name = ""
    env_key = ""
    fields: tuple[str, ...] = ()

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def fetch(self, day: date, key: str) -> dict[str, np.ndarray]:
        return self.parse(self.request(day, key), day)

    def request(self, day: date, key: str):
        raise NotImplementedError

    def parse(self, payload, day: date) -> dict[str, np.ndarray]:
        raise NotImplementedError

    def _get(self, params: dict):
        import requests
        r = requests.get(self.cfg["url"], params=params, timeout=30,
                         headers={"Accept": "application/json"})
        r.raise_for_status()
        return r.json()


class CimisAdapter(Adapter):
    name, env_key, fields = "CIMIS", "CIMIS_APPKEY", ("temp_f", "rh", "solar_wm2")

    def request(self, day, key):
        c = self.cfg
        return self._get({"appKey": key, "targets": c["station"], "startDate": day.isoformat(),
                          "endDate": day.isoformat(), "unitOfMeasure": c["units"],
                          "dataItems": ",".join(c["data_items"][f] for f in self.fields)})

    def parse(self, payload, day):
        out = {f: np.full(24, np.nan) for f in self.fields}
        names = self.cfg["response_fields"]
        for rec in payload["Data"]["Providers"][0]["Records"]:
            h = int(rec["Hour"]) // 100 - 1  # "0100" = hour ending 01:00 -> index 0 (CIMIS uses PST; unverified)
            if not 0 <= h < 24:
                continue
            for f in self.fields:
                v = (rec.get(names[f]) or {}).get("Value")
                if v not in (None, ""):
                    out[f][h] = float(v)
        out["temp_f"] = out["temp_f"] * 9 / 5 + 32  # metric request: C -> F
        return out


class AirNowAdapter(Adapter):
    name, env_key, fields = "AirNow", "AIRNOW_KEY", ("pm25_ugm3",)

    def _utc_start(self, day):
        return datetime.combine(day, time(0)) - timedelta(hours=self.cfg["utc_offset_hours"])

    def request(self, day, key):
        start = self._utc_start(day)
        end = start + timedelta(hours=23)
        return self._get({"startDate": start.strftime("%Y-%m-%dT%H"), "endDate": end.strftime("%Y-%m-%dT%H"),
                          "parameters": "PM25", "BBOX": self.cfg["bbox"], "dataType": "C",
                          "format": "application/json", "API_KEY": key})

    def parse(self, payload, day):
        sums, counts = np.zeros(24), np.zeros(24)
        for rec in payload:
            local = datetime.strptime(rec["UTC"], "%Y-%m-%dT%H:%M") + timedelta(hours=self.cfg["utc_offset_hours"])
            v = rec.get("Value")
            if local.date() != day or v is None or v < 0:  # AirNow uses negative sentinels for missing
                continue
            sums[local.hour] += v
            counts[local.hour] += 1
        return {"pm25_ugm3": np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)}


def hourly_to_slots(values: np.ndarray, max_missing: int, field: str) -> list[float]:
    """Interpolate up to max_missing missing hours, then repeat each hour across its slots."""
    ok = ~np.isnan(values)
    if (~ok).sum() > max_missing:
        raise ValueError(f"{field}: {(~ok).sum()} of 24 hours missing (max {max_missing})")
    hours = np.arange(24)
    filled = np.interp(hours, hours[ok], values[ok])
    return np.round(np.repeat(filled, SLOTS_PER_DAY // 24), 2).tolist()


def build_day(day: date, adapters: list[Adapter], keys: dict[str, str], cfg: dict) -> DayRecord:
    fields = {}
    for a in adapters:
        for f, v in a.fetch(day, keys[a.env_key]).items():
            fields[f] = hourly_to_slots(v, cfg["max_missing_hours"], f)
    sources = "+".join(a.name for a in adapters)
    return DayRecord(id=f"real-{day.isoformat()}-{cfg['region']}", label=f"{sources} observed {day.isoformat()}",
                     region=cfg["region"], provenance="real_cached", date=day.isoformat(), **fields)


def make_adapters(cfg: dict) -> list[Adapter]:
    return [CimisAdapter(cfg["cimis"]), AirNowAdapter(cfg["airnow"])]


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
