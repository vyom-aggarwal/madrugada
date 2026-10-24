"""Phase 1: PM2.5 -> AQI conversion from config breakpoints."""
import numpy as np
import pytest

from app.aqi import (extrapolation_warning, load_breakpoints, pm25_to_aqi,
                     pm25_to_aqi_scalar, truncate_pm25)


@pytest.mark.parametrize("pm, expected", [(9.0, 50), (35.4, 100), (55.5, 151)])
def test_required_breakpoint_values(pm, expected):
    assert pm25_to_aqi_scalar(pm) == (expected, False)


def test_breakpoint_edges_from_config():
    bp = load_breakpoints()
    for pm_lo, pm_hi, aqi_lo, aqi_hi in bp:
        assert pm25_to_aqi_scalar(pm_lo)[0] == aqi_lo
        assert pm25_to_aqi_scalar(pm_hi)[0] == aqi_hi


def test_truncation_before_lookup():
    # 9.09 truncates to 9.0 (AQI 50), not rounds to 9.1 (AQI 51)
    assert pm25_to_aqi_scalar(9.09)[0] == 50
    assert pm25_to_aqi_scalar(35.49)[0] == 100
    assert truncate_pm25([2.3, 0.3, 12.19])[0] == pytest.approx(2.3)
    assert truncate_pm25([12.19])[0] == pytest.approx(12.1)


def test_above_top_is_extrapolated_and_flagged_not_clipped():
    bp = load_breakpoints()
    top_pm, top_aqi = bp[-1, 1], bp[-1, 3]
    aqi_hi, flag_hi = pm25_to_aqi_scalar(top_pm + 100)
    assert flag_hi and aqi_hi > top_aqi
    slope = (bp[-1, 3] - bp[-1, 2]) / (bp[-1, 1] - bp[-1, 0])
    assert aqi_hi == round(top_aqi + slope * 100)
    assert pm25_to_aqi_scalar(top_pm) == (int(top_aqi), False)


def test_vectorized_and_warning():
    r = pm25_to_aqi(np.array([-3.0, 0.0, 12.0, 500.0]))
    assert r.aqi[0] == 0 and r.aqi[1] == 0
    assert r.extrapolated.tolist() == [False, False, False, True]
    assert "extrapolated" in extrapolation_warning(r)
    assert extrapolation_warning(pm25_to_aqi([10.0])) is None
