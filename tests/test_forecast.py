"""Forecast proxy: leakage safety, formula, and ORACLE labeling."""
import numpy as np
import pytest

from app.forecast import FIELDS, forecast


def _poisoned(d, value=999.0):
    return d.model_copy(deep=True, update={k: [value] * 96 for k in FIELDS})


def test_changing_day_d_does_not_change_forecast(test_days, history):
    i = 2
    target = test_days[i]
    pool = history + test_days
    before = forecast(target, pool)
    # Poison day D (both the target arg and its copy in the pool) and every later day.
    bad_target = _poisoned(target)
    bad_pool = history + test_days[:i] + [bad_target] + [_poisoned(d) for d in test_days[i + 1:]]
    after = forecast(bad_target, bad_pool)
    assert before.method == after.method == "FORECAST"
    for k in FIELDS:
        assert getattr(before.day, k) == getattr(after.day, k)
    assert target.date not in before.source_dates


def test_changing_day_d_minus_1_does_change_forecast(test_days, history):
    i = 2
    pool = history + test_days[:i - 1] + [_poisoned(test_days[i - 1])] + test_days[i:]
    assert forecast(test_days[i], pool).day.temp_f != forecast(test_days[i], history + test_days).day.temp_f


def test_formula(test_days, history):
    target = test_days[0]
    r = forecast(target, history + test_days)
    prev = np.array(history[-1].temp_f)
    mean = np.mean([h.temp_f for h in history[-7:]], axis=0)
    assert np.allclose(r.day.temp_f, 0.5 * prev + 0.5 * mean, atol=1e-3)
    assert r.day.provenance == "synthetic" and r.day.label.startswith("FORECAST")


def test_oracle_returns_truth_and_is_labeled(test_days, history):
    target = test_days[3]
    r = forecast(target, history + test_days, oracle=True)
    assert r.method == "ORACLE" and r.day.label.startswith("ORACLE") and "oracle" in r.day.id
    for k in FIELDS:
        assert getattr(r.day, k) == getattr(target, k)


def test_insufficient_history_raises(history):
    with pytest.raises(ValueError, match="needs prior days"):
        forecast(history[3], history)
