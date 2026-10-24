"""Phase 2: exposure, baselines, optimizer, Pareto. Fixtures are SYNTHETIC illustrations, not evidence."""
import itertools
import time

import numpy as np
import pytest

from app.baselines import b1, b2, b3
from app.exposure import day_arrays, exposure, plan_cost
from app.models import Block
from app.optimizer import dominates, optimize, pareto, search

TARGET = 8.5


def _blocks(plan):
    return [(b.start_slot, b.end_slot) for b in plan.blocks]


def test_exposure_hours_hand_check():
    t = np.array([70, 85, 96, 96, 91, 91, 70, 70], dtype=float)
    a = np.array([50, 50, 50, 160, 120, 50, 151, 101], dtype=float)
    m = exposure(t, a, [Block(start_slot=0, end_slot=8)])
    assert (m.hours_ge_80f, m.hours_ge_95f) == (1.25, 0.5)
    assert (m.hours_aqi_ge_101, m.hours_aqi_ge_151) == (1.0, 0.5)
    assert (m.dual_hazard_hours, m.paid_hours) == (0.5, 2.0)


def test_a_cooccurring_optimizer_cost_below_b1(scenarios):
    t, a = day_arrays(scenarios["co_occurring"])
    assert optimize(t, a).cost < b1(t, a).cost


@pytest.mark.parametrize("target", [8.5, 8.0, 7.3, 6.8, 4.0])
def test_b_paid_hours_never_below_target(scenarios, target):
    for day in scenarios.values():
        t, a = day_arrays(day)
        for plan in (optimize(t, a, paid_hours_target=target), b3(t, a, paid_hours_target=target)):
            assert exposure(t, a, plan.blocks).paid_hours >= target
    for p in pareto(*day_arrays(scenarios["co_occurring"])):
        assert p.paid_hours >= p.paid_fraction * TARGET - 1e-9


@pytest.mark.xfail(strict=True, reason=(
    "Fixture shape: on smoke_only, AQI >= 101 covers 05:45-19:00, so only 1.75 h of the window is below 101 "
    "and every 8.5 h plan has >= 6.75 smoke hours. B3 (no heat signal) tie-breaks to the earliest start, "
    "04:00, and captures all of the clean hours too: both plans have 6.75 h. Dual optimizer still wins on "
    "AQI>=151 (4.75 vs 5.0 h) and cost (66 vs 67). Not fixed by editing fixtures or weights (CLAUDE.md)."))
def test_c_smoke_only_b3_has_more_smoke_hours(scenarios):
    t, a = day_arrays(scenarios["smoke_only"])
    dual = exposure(t, a, optimize(t, a).blocks)
    heat_only = exposure(t, a, b3(t, a).blocks)
    assert heat_only.hours_aqi_ge_101 > dual.hours_aqi_ge_101


def _brute(cost, n, e, l, mb, mg):
    """Plain-Python enumeration with the same tie-break key as search()."""
    best = None
    for s in range(e, l - n + 1):
        key = (round(sum(cost[s:s + n]), 9), 1, s, s + n, -1)
        best = min(best or key, key)
    for a in range(mb, n - mb + 1):
        b = n - a
        for s1, s2 in itertools.product(range(e, l), repeat=2):
            if s2 >= s1 + a + mg and s2 + b <= l:
                key = (round(sum(cost[s1:s1 + a]) + sum(cost[s2:s2 + b]), 9), 2, s1, s1 + a, s2)
                best = min(best or key, key)
    blocks = [(best[2], best[3])] + ([(best[4], best[4] + n - (best[3] - best[2]))] if best[1] == 2 else [])
    return best[0], blocks


@pytest.mark.parametrize("seed", range(8))
def test_d_brute_force_matches_on_tiny_grid(seed):
    rng = np.random.default_rng(seed)
    cost = rng.integers(0, 4, 24).astype(float)  # small integer costs -> many ties
    for n, e, l, mb, mg in [(10, 2, 22, 3, 2), (8, 0, 24, 2, 1), (12, 1, 20, 4, 3)]:
        got_cost, got_blocks = search(cost, n, e, l, mb, mg)
        exp_cost, exp_blocks = _brute(list(cost), n, e, l, mb, mg)
        assert (round(got_cost, 9), got_blocks) == (exp_cost, exp_blocks)


def test_e_early_pm25_peak_plan_differs_from_b2(scenarios):
    t, a = day_arrays(scenarios["early_pm25_peak"])
    assert _blocks(optimize(t, a)) != _blocks(b2(t, a))


@pytest.mark.parametrize("name", ["heat_only", "smoke_only", "co_occurring", "co_occurring_offset"])
def test_f_pareto_has_no_dominated_points(scenarios, name):
    pts = pareto(*day_arrays(scenarios[name]))
    assert pts
    assert not any(dominates(q, p) for p in pts for q in pts)
    assert len({(p.heat_hours, p.smoke_hours, p.paid_hours) for p in pts}) == len(pts)


def test_g_deterministic(scenarios):
    t, a = day_arrays(scenarios["co_occurring_offset"])
    runs = [optimize(t, a).model_dump() for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]
    assert [p.model_dump() for p in pareto(t, a)] == [p.model_dump() for p in pareto(t, a)]


def test_optimize_under_one_second(scenarios):
    t, a = day_arrays(scenarios["co_occurring"])
    start = time.perf_counter()
    optimize(t, a)
    assert time.perf_counter() - start < 1.0


def test_plan_cost_matches_search_cost(scenarios):
    t, a = day_arrays(scenarios["co_occurring"])
    plan = optimize(t, a)
    assert plan.cost == pytest.approx(plan_cost(plan.blocks, t, a))
