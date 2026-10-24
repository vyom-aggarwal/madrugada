"""HTTP fetching for the real-data job: raw-response cache (resume without re-downloading), a minimum
interval between calls, and exponential backoff on 429/5xx/network errors.

Error messages never include request parameters or URLs with parameters (API keys).
"""
import json
import time
from pathlib import Path


class FetchError(RuntimeError):
    pass


class Fetcher:
    def __init__(self, raw_dir: Path, throttle: dict, sleep=time.sleep, clock=time.monotonic):
        self.raw_dir, self.t, self.sleep, self.clock, self.last = raw_dir, throttle, sleep, clock, -1e9
        self.network_calls = 0

    def _request(self, url: str, params: dict, cache_key: str, headers: dict | None = None, stream: bool = False):
        import requests
        for attempt in range(self.t["max_retries"] + 1):
            wait = self.t["min_interval_s"] - (self.clock() - self.last)
            if wait > 0:
                self.sleep(wait)
            self.last = self.clock()
            self.network_calls += 1
            try:
                r = requests.get(url, params=params, timeout=120, headers=headers or {}, stream=stream)
                retry, err = r.status_code == 429 or r.status_code >= 500, f"HTTP {r.status_code}"
                if 400 <= r.status_code < 500 and not retry:
                    raise FetchError(f"{cache_key}: {err} (not retried)")
                if not retry:
                    return r
            except requests.RequestException as e:
                retry, err = True, e.__class__.__name__
            if attempt == self.t["max_retries"]:
                raise FetchError(f"{cache_key}: {err} after {attempt + 1} attempts")
            self.sleep(self.t["backoff_base_s"] * 2 ** attempt)

    def _cached(self, cache_key: str, suffix: str) -> Path:
        return self.raw_dir / f"{cache_key}{suffix}"

    def get(self, url: str, params: dict, cache_key: str):
        """JSON response, cached as <cache_key>.json."""
        path = self._cached(cache_key, ".json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        data = self._request(url, params, cache_key, {"Accept": "application/json"}).json()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return data

    def get_text(self, url: str, params: dict, cache_key: str, suffix: str = ".txt") -> str:
        path = self._cached(cache_key, suffix)
        if path.exists():
            return path.read_text(encoding="utf-8")
        text = self._request(url, params, cache_key).text
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return text

    def download(self, url: str, cache_key: str, suffix: str) -> Path:
        """Stream a (large) file to the cache once; later calls return the cached path."""
        path = self._cached(cache_key, suffix)
        if path.exists():
            return path
        r = self._request(url, {}, cache_key, stream=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_suffix(path.suffix + ".part")
        with open(part, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
        part.replace(path)
        return path
