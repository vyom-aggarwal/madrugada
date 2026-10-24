import json
from pathlib import Path

import pytest

from app.models import DayRecord

FIXTURES = Path(__file__).resolve().parent.parent / "data" / "fixtures"


@pytest.fixture(autouse=True)
def isolate_real_cache(tmp_path_factory, monkeypatch):
    """Tests never see locally downloaded real days (data/cache is gitignored and may hold thousands)."""
    from app import planning
    from eval import run_eval
    empty = tmp_path_factory.mktemp("empty_cache")
    monkeypatch.setattr(planning, "CACHE", empty)
    monkeypatch.setattr(run_eval, "MANIFEST", empty / "manifest.json")
    cached = (planning.load_days, planning.rule_selected_day)  # originals; tests may monkeypatch them
    for f in cached:
        f.cache_clear()
    yield
    for f in cached:
        f.cache_clear()


def load_raw(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def test_days() -> list[DayRecord]:
    return [DayRecord(**d) for d in load_raw("days.json")]


@pytest.fixture
def scenarios(test_days) -> dict[str, DayRecord]:
    """Test days keyed by scenario name (id 'syn-YYYY-MM-DD-<name>')."""
    return {d.id.split("-", 4)[-1]: d for d in test_days}


@pytest.fixture
def history() -> list[DayRecord]:
    return [DayRecord(**d) for d in load_raw("history.json")]
