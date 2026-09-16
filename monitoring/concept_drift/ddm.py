"""
Drift Detection Method (DDM) for streaming error rate drift.
"""

import numpy as np
from typing import Tuple, List


class DDM:
    """Drift Detection Method (DDM) algorithm."""

    def __init__(
        self,
        min_num_instances: int = 30,
        warning_level: float = 2.0,
        drift_level: float = 3.0,
    ):
        self.min_num_instances = min_num_instances
        self.warning_level = warning_level
        self.drift_level = drift_level
        self.reset()

    def reset(self) -> None:
        self.sample_count = 0
        self.error_count = 0
        self.p = 0.0
        self.s = 0.0
        self.p_min = float("inf")
        self.s_min = float("inf")
        self.p_plus_s_min = float("inf")
        self.warning_detected = False
        self.drift_detected = False

    def add_element(self, is_error: int) -> Tuple[bool, bool]:
        """Adds a single binary error sample (1 for error, 0 for correct prediction). Returns (warning, drift)."""
        self.sample_count += 1
        self.error_count += is_error

        self.p = self.error_count / self.sample_count
        self.s = np.sqrt(self.p * (1.0 - self.p) / self.sample_count)

        if self.sample_count < self.min_num_instances:
            return False, False

        p_plus_s = self.p + self.s

        if p_plus_s < self.p_plus_s_min:
            self.p_min = self.p
            self.s_min = self.s
            self.p_plus_s_min = p_plus_s

        self.warning_detected = p_plus_s >= self.p_min + self.warning_level * self.s_min
        self.drift_detected = p_plus_s >= self.p_min + self.drift_level * self.s_min

        return self.warning_detected, self.drift_detected

    def run_batch(self, errors: np.ndarray) -> Tuple[bool, bool, int]:
        """Processes a sequence of error signals and returns (warning, drift, first_drift_index)."""
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
