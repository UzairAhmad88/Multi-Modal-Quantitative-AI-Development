"""
Page-Hinkley cumulative sum change-point detector.
"""

import numpy as np
from typing import Tuple


class PageHinkley:
    """Page-Hinkley cumulative sum change-point test."""

    def __init__(
        self,
        delta: float = 0.005,
        threshold: float = 50.0,
        alpha: float = 0.9999,
    ):
        self.delta = delta
        self.threshold = threshold
        self.alpha = alpha
        self.reset()

    def reset(self) -> None:
        self.sample_count = 0
        self.sum = 0.0
        self.mean = 0.0
        self.cum_sum = 0.0
        self.min_cum_sum = 0.0
        self.drift_detected = False

    def add_element(self, value: float) -> bool:
        """Adds a single continuous observation. Returns True if drift/change-point detected."""
        self.sample_count += 1
        self.mean = self.mean + (value - self.mean) / self.sample_count
        self.cum_sum = self.cum_sum + (value - self.mean - self.delta)

        if self.cum_sum < self.min_cum_sum:
            self.min_cum_sum = self.cum_sum

        self.drift_detected = (self.cum_sum - self.min_cum_sum) > self.threshold
        return self.drift_detected

    def run_batch(self, values: np.ndarray) -> Tuple[bool, int]:
        self.reset()
        drift_idx = -1
        any_drift = False

        for idx, val in enumerate(values):
            d = self.add_element(float(val))
            if d:
                any_drift = True
                if drift_idx == -1:
                    drift_idx = idx

        return any_drift, drift_idx
