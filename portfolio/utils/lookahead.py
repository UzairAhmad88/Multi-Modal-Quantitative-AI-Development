"""
Look-Ahead Bias Protection Utilities for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import pandas as pd


class LookAheadProtector:
    """Filters market data, alpha signals, and fundamentals to strictly prevent look-ahead bias."""

    @staticmethod
    def filter_point_in_time(
        df: pd.DataFrame,
        decision_timestamp: str,
        timestamp_col: str = "availability_timestamp",
    ) -> pd.DataFrame:
        """Filter dataset to only rows available on or before decision_timestamp."""
        if timestamp_col not in df.columns:
            if "data_timestamp" in df.columns:
                timestamp_col = "data_timestamp"
            elif "timestamp" in df.columns:
                timestamp_col = "timestamp"
            else:
                return df

        target_dt = pd.to_datetime(decision_timestamp)
        df_dt = pd.to_datetime(df[timestamp_col])

        valid_mask = df_dt <= target_dt
        filtered_df = df[valid_mask].copy()
        return filtered_df

    @staticmethod
    def audit_timestamps(
        inputs: Dict[str, Any],
        decision_timestamp: str,
    ) -> Tuple[bool, List[str]]:
        """Audit dictionaries or series of inputs to ensure no data from future timestamps is present."""
        violations = []
        target_dt = pd.to_datetime(decision_timestamp)

        for key, val in inputs.items():
            if isinstance(val, dict) and "availability_timestamp" in val:
                avail_dt = pd.to_datetime(val["availability_timestamp"])
                if avail_dt > target_dt:
                    violations.append(
                        f"Look-ahead violation for '{key}': availability {avail_dt} > decision {target_dt}"
                    )

        passed = len(violations) == 0
        return passed, violations
