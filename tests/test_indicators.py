import math
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from src.indicators import ParkinsonVolatility, SlidingMonotonicExtremum


def test_parkinson_volatility_zero_spread():
    pv = ParkinsonVolatility(window_size=10)
    # High == Low -> Zero volatility
    for _ in range(10):
        vol = pv.update(100.0, 100.0)
        assert vol == 0.0
        assert pv.volatility_bps(100.0, 100.0) == 0.0


def test_parkinson_volatility_known_values():
    pv = ParkinsonVolatility(window_size=4)
    # Feed 10% daily range: High=110, Low=100 -> ratio = 1.1
    # expected log(1.1) = 0.09531018
    # variance = (1 / (4 * ln(2))) * (0.09531018)^2 = 0.36067376 * 0.00908403 = 0.00327637
    # stdev = sqrt(0.00327637) = 0.0572396
    for _ in range(4):
        vol = pv.update(110.0, 100.0)
    
    assert abs(vol - 0.0572396) < 1e-4
    assert abs(pv.volatility_bps(110.0, 100.0) - 572.396) < 1.0


def test_monotonic_deque_sliding_maximum():
    sme = SlidingMonotonicExtremum(window_size=3, find_max=True)
    # Stream: [10, 5, 12, 8, 15]
    assert sme.push(10.0) == 10.0
    assert sme.push(5.0) == 10.0
    assert sme.push(12.0) == 12.0  # Window: [10, 5, 12] -> max = 12
    assert sme.push(8.0) == 12.0   # Window: [5, 12, 8] -> max = 12
    assert sme.push(7.0) == 12.0   # Window: [12, 8, 7] -> max = 12
    assert sme.push(9.0) == 9.0    # Window: [8, 7, 9] (12 expired) -> max = 9.0


def test_monotonic_deque_sliding_minimum():
    sme = SlidingMonotonicExtremum(window_size=3, find_max=False)
    # Stream: [10, 5, 12, 8, 3]
    assert sme.push(10.0) == 10.0
    assert sme.push(5.0) == 5.0
    assert sme.push(12.0) == 5.0   # Window: [10, 5, 12] -> min = 5
    assert sme.push(8.0) == 5.0    # Window: [5, 12, 8] -> min = 5
    assert sme.push(9.0) == 8.0    # Window: [12, 8, 9] (5 expired) -> min = 8.0
    assert sme.push(3.0) == 3.0    # Window: [8, 9, 3] -> min = 3.0


def test_parkinson_volatility_floating_point_drift_resilience():
    """Verify that 10,000 continuous sliding updates do not trigger floating-point drift or assert failure."""
    pv = ParkinsonVolatility(window_size=20)
    for i in range(10000):
        # Alternate between tight and wide spreads to test repeated addition/subtraction
        spread = 1.0 + (0.01 * (i % 7))
        low = 100.0 + (i % 13)
        high = low * spread
        vol = pv.update(high, low)
        assert not math.isnan(vol)
        assert vol >= 0.0
        assert pv._sum_hl_sq >= 0.0

