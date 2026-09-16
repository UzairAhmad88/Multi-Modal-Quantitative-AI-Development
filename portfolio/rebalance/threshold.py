"""
Threshold-Based Rebalance Engine for Portfolio Construction OS.
"""

from typing import Dict, Any, Tuple


class ThresholdRebalancer:
    """Evaluates whether weight drift exceeds configured tolerance thresholds."""

    @staticmethod
    def should_rebalance_threshold(
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        threshold: float = 0.05,
    ) -> Tuple[bool, float]:
        all_assets = set(current_weights.keys()).union(target_weights.keys())
        max_drift = 0.0

        for a in all_assets:
            w_curr = current_weights.get(a, 0.0)
            w_targ = target_weights.get(a, 0.0)
            drift = abs(w_targ - w_curr)
            if drift > max_drift:
                max_drift = drift

        should_rebal = max_drift >= threshold
        return should_rebal, float(max_drift)
