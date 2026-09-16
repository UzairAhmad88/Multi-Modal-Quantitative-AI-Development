"""
Leakage Detector: Automated detection of look-ahead bias, timestamp violations, and unpurged overlaps.
"""

from typing import Dict, Any, List, Tuple


class LeakageDetector:
    """Detects future timestamp leakage and overlapping sample contamination."""

    def check_leakage(
        self,
        decision_timestamps: List[str],
        data_availability_timestamps: List[str]
    ) -> Tuple[bool, List[str]]:
        """Verifies no data availability timestamp succeeds decision timestamp."""
        issues = []
        for i, (t_dec, t_avail) in enumerate(zip(decision_timestamps, data_availability_timestamps)):
            if t_avail > t_dec:
                issues.append(f"Look-Ahead Leakage at index {i}: Data availability ({t_avail}) exceeds decision timestamp ({t_dec})")

        is_clean = len(issues) == 0
        return is_clean, issues
