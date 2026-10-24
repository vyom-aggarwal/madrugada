"""PurpleAir EPA US-wide correction: 0.524*pm_cf1 - 0.0862*RH + 5.75 (values from config.yaml)."""
import numpy as np
import pytest

from app.aqi import purpleair_correct

# Hand-computed:
#   10, 50  -> 5.24  - 4.31  + 5.75 = 6.68
#   100, 30 -> 52.4  - 2.586 + 5.75 = 55.564
#   300, 60 -> 157.2 - 5.172 + 5.75 = 157.778
HAND = [(10, 50, 6.68), (100, 30, 55.564), (300, 60, 157.778)]


@pytest.mark.parametrize("pm, rh, expected", HAND)
def test_scalar_hand_computed(pm, rh, expected):
    r = purpleair_correct(pm, rh)
    assert float(r.values) == pytest.approx(expected)
    assert not bool(r.correction_underestimates_high_smoke)
    assert r.warning is None


def test_array_matches_hand_computed():
    pm, rh, expected = map(np.array, zip(*HAND))
    r = purpleair_correct(pm, rh)
    assert r.values == pytest.approx(expected)


def test_above_250_flagged_with_warning():
    # 500, 20 -> 262 - 1.724 + 5.75 = 266.026 (flag); 466, 0 -> 249.934 (no flag)
    r = purpleair_correct([500, 466, 10], [20, 0, 50])
    assert r.values[0] == pytest.approx(266.026)
    assert r.correction_underestimates_high_smoke.tolist() == [True, False, False]
    assert "1 slot(s)" in r.warning and "underestimates" in r.warning


def test_scalar_rh_broadcasts():
    r = purpleair_correct([10, 100], 50)
    assert r.values.shape == (2,)
