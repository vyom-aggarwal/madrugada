"""Robust planner: leakage safety, fallback, constraints."""
import numpy as np

from app.aqi import pm25_to_aqi
from app.exposure import exposure
from app.forecast import FIELDS, forecast
from app.optimizer import optimize
from app.robust import FALLBACK_FLAG, robust_plan


def _poisoned(d, value=999.0):
    return d.model_copy(deep=True, update={k: [value] * 96 for k in FIELDS})


def _key(r):
    return (r.plan.model_dump(), r.uncertainty, r.flags, r.residual_dates)


def test_robust_uses_no_day_d_data(test_days, history):
    i = 2
    pool = history + test_days
    before = robust_plan(test_days[i], pool)
    assert not before.flags and before.uncertainty["n_scenarios"] >= 7
    bad_pool = history + test_days[:i] + [_poisoned(d) for d in test_days[i:]]
    after = robust_plan(_poisoned(test_days[i]), bad_pool)
    assert _key(before) == _key(after)
    assert test_days[i].date not in before.residual_dates


def test_changing_d_minus_1_may_change_robust(test_days, history):
    i = 2
    pool = history + test_days
    changed = history + test_days[:i - 1] + [_poisoned(test_days[i - 1], 120.0)] + test_days[i:]
    assert _key(robust_plan(test_days[i], pool)) != _key(robust_plan(test_days[i], changed))


def test_fallback_with_short_history(history):
    target = history[8]  # 2025-07-26: has a proxy forecast, but only 1 prior day with its own forecast
    r = robust_plan(target, history)
    assert r.flags == [FALLBACK_FLAG] and r.uncertainty is None
    fc = forecast(target, history)
    expected = optimize(np.asarray(fc.day.temp_f), pm25_to_aqi(fc.day.pm25_ugm3).aqi)
    assert [b.model_dump() for b in r.plan.blocks] == [b.model_dump() for b in expected.blocks]


def test_robust_respects_paid_hours_and_reports_uncertainty(test_days, history):
    r = robust_plan(test_days[5], history + test_days, paid_hours_target=7.3)
    t = np.array(test_days[5].temp_f)
    assert exposure(t, t, r.plan.blocks).paid_hours >= 7.3
    u = r.uncertainty
    for k in ("hours_ge_95f", "hours_aqi_ge_101"):
        assert set(u[k]) == {"mean", "p90"}
        assert 0 <= u[k]["mean"] <= 7.5 and 0 <= u[k]["p90"] <= 7.5  # hours within the 7.5 h plan
