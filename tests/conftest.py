import json
from pathlib import Path

import pytest

from app.models import DayRecord

FIXTURES = Path(__file__).resolve().parent.parent / "data" / "fixtures"


def load_raw(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def test_days() -> list[DayRecord]:
    return [DayRecord(**d) for d in load_raw("days.json")]


@pytest.fixture
def history() -> list[DayRecord]:
    return [DayRecord(**d) for d in load_raw("history.json")]
