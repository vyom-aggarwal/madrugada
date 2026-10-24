"""B3 tie-break variants: optimizer cost bounds them, and both are deterministic."""
import numpy as np
import pytest

from app.baselines import b3, b3_early, b3_late
from app.exposure import day_arrays
from app.optimizer import optimize, search

NAMES = ["heat_only", "smoke_only", "co_occurring", "early_pm25_peak", "mild", "co_occurring_offset"]


@pytest.mark.parametrize("name", NAMES)
def test_optimizer_cost_le_both_b3_variants(scenarios, name):
    t, a = day_arrays(scenarios[name])
    opt = optimize(t, a).cost
    assert opt <= b3_early(t, a).cost + 1e-9
    assert opt <= b3_late(t, a).cost + 1e-9


@pytest.mark.parametrize("fn", [b3_early, b3_late])
def test_b3_variants_deterministic(scenarios, fn):
    for day in scenarios.values():
        t, a = day_arrays(day)
        runs = [fn(t, a).model_dump() for _ in range(3)]
        assert runs[0] == runs[1] == runs[2]


def test_b3_name_is_early_policy(scenarios):
    t, a = day_arrays(scenarios["mild"])
    assert b3(t, a).blocks == b3_early(t, a).blocks and b3(t, a).name == "B3"


def test_late_tie_break_picks_latest_start_on_flat_cost():
    cost = np.zeros(40)
    assert search(cost, 10, 0, 40, 4, 2, tie_break="early") == (0.0, [(0, 10)])
    assert search(cost, 10, 0, 40, 4, 2, tie_break="late") == (0.0, [(30, 40)])
