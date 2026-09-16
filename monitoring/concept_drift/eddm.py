"""
Early Drift Detection Method (EDDM) for tracking distance between errors.
"""

import numpy as np
from typing import Tuple


class EDDM:
    """Early Drift Detection Method (EDDM)."""

    def __init__(
        self,
        min_num_errors: int = 30,
        warning_level: float = 0.95,
        drift_level: float = 0.90,
    ):
        self.min_num_errors = min_num_errors
        self.warning_level = warning_level
        self.drift_level = drift_level
        self.reset()

    def reset(self) -> None:
        self.sample_count = 0
        self.error_count = 0
        self.last_error_instance = 0
        self.distance_sum = 0.0
        self.distance_sq_sum = 0.0
        self.max_ratio = float("-inf")
        self.warning_detected = False
        self.drift_detected = False

    def add_element(self, is_error: int) -> Tuple[bool, bool]:
        """Adds a single error observation (1 for error, 0 for correct). Returns (warning, drift)."""
        self.sample_count += 1

        if is_error == 1:
            self.error_count += 1
            if self.error_count > 1:
                dist = self.sample_count - self.last_error_instance
                self.distance_sum += dist
                self.distance_sq_sum += dist * dist

                n = self.error_count - 1
                mean_dist = self.distance_sum / n
                var_dist = (self.distance_sq_sum / n) - (mean_dist * mean_dist)
                std_dist = np.sqrt(max(var_dist, 0.0))

                ratio_val = mean_dist + 2.0 * std_dist
                if ratio_val > self.max_ratio:
                    self.max_ratio = ratio_val

                if self.error_count >= self.min_num_errors and self.max_ratio > 0:
                    current_ratio = ratio_val / self.max_ratio
                    self.warning_detected = current_ratio < self.warning_level
                    self.drift_detected = current_ratio < self.drift_level

            self.last_error_instance = self.sample_count

        return self.warning_detected, self.drift_detected

    def run_batch(self, errors: np.ndarray) -> Tuple[bool, bool, int]:
        self.reset()
        drift_idx = -1
        any_warning = False
        any_drift = False

        for idx, err in enumerate(errors):
            w, d = self.add_element(int(err))
            if w:
                any_warning = True
            if d:
                any_drift = True
                if drift_idx == -1:
                    drift_idx = idx

        return any_warning, any_drift, drift_idx
