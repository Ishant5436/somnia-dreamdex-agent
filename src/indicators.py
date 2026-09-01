"""
High-Performance Quantitative Indicators & Monotonic Window Primitives
Optimized for zero-allocation O(1) amortized latency on event volatility evaluation.
"""

import math
from collections import deque


class ParkinsonVolatility:
    """
    Parkinson High-Low Realized Volatility Estimator.
    Invariant: 5x more efficient variance estimation than close-to-close returns.
    Formula: sigma_parkinson = sqrt( 1 / (4 * ln(2) * N) * sum( (ln(H_i / L_i))^2 ) )
    """
    PARKINSON_CONSTANT = 1.0 / (4.0 * math.log(2.0))

    def __init__(self, window_size: int = 30):
        assert window_size > 0, "Window size must be positive"
        self.window_size = window_size
        self._hl_squared_logs: deque[float] = deque(maxlen=window_size)
        self._sum_hl_sq: float = 0.0

    def update(self, high: float, low: float) -> float:
        assert high >= low > 0.0, "High must be >= Low > 0.0"
        
        ratio = math.log(high / low)
        hl_sq = ratio * ratio

        if len(self._hl_squared_logs) == self.window_size:
            evicted = self._hl_squared_logs.popleft()
            self._sum_hl_sq -= evicted

        self._hl_squared_logs.append(hl_sq)
        self._sum_hl_sq += hl_sq
        assert self._sum_hl_sq >= 0.0

        n = len(self._hl_squared_logs)
        variance = (self.PARKINSON_CONSTANT * self._sum_hl_sq) / max(n, 1)
        return math.sqrt(variance)

    def volatility_bps(self, high: float, low: float) -> float:
        """Returns volatility in basis points (1 bps = 0.01%)."""
        vol = self.update(high, low)
        return vol * 10000.0


class SlidingMonotonicExtremum:
    """
    Monotonic Deque for O(1) Amortized Sliding Window Maximum and Minimum.
    Maintains index-tagged elements in strict monotonic order.
    """
    def __init__(self, window_size: int = 50, find_max: bool = True):
        assert window_size > 0, "Window size must be positive"
        self.window_size = window_size
        self.find_max = find_max
        self._deque: deque[tuple[float, int]] = deque()
        self._current_index = 0

    def push(self, val: float) -> float:
        idx = self._current_index
        self._current_index += 1

        # Evict expired elements outside the rolling window
        min_valid = idx - self.window_size + 1
        while self._deque and self._deque[0][1] < min_valid:
            self._deque.popleft()

        # Monotonic eviction
        if self.find_max:
            while self._deque and self._deque[-1][0] <= val:
                self._deque.pop()
        else:
            while self._deque and self._deque[-1][0] >= val:
                self._deque.pop()

        self._deque.append((val, idx))
        return self._deque[0][0]

    @property
    def extremum(self) -> float:
        assert len(self._deque) > 0, "Deque is empty"
        return self._deque[0][0]
