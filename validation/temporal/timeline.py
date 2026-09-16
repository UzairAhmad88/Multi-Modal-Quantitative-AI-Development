"""
Timeline Diagnostics & Timestamp Inspector for Walk-Forward OS.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class TimelineValidator:
    """Audits data timelines for strict chronological ordering and point-in-time availability."""

    @staticmethod
    def audit_timeline(
        df: pd.DataFrame,
        timestamp_col: str = "timestamp",
        availability_col: Optional[str] = "availability_timestamp",
        label_horizon_steps: int = 1,
    ) -> Dict[str, Any]:
        """Audits time series for duplicate timestamps, monotonic sorting, and availability lags."""
        issues: List[str] = []
        n = len(df)

        if timestamp_col not in df.columns:
            return {"status": "SKIPPED", "reason": f"Timestamp column '{timestamp_col}' missing"}

        ts = pd.to_datetime(df[timestamp_col])

        # 1. Monotonic sorting check
        is_sorted = bool(ts.is_monotonic_increasing)
        if not is_sorted:
            issues.append("TIMELINE_UNSORTED: Datetime index is not monotonically increasing.")

        # 2. Duplicate decision timestamps
        duplicates = int(ts.duplicated().sum())
        if duplicates > 0:
            issues.append(f"DUPLICATE_TIMESTAMPS: Found {duplicates} duplicate decision timestamps.")

        # 3. Availability timestamp check (Point-in-Time compliance)
        availability_violations = 0
        if availability_col and availability_col in df.columns:
            avail = pd.to_datetime(df[availability_col])
            future_avail = avail > ts
            availability_violations = int(future_avail.sum())
            if availability_violations > 0:
                issues.append(
                    f"AVAILABILITY_LEAKAGE: Found {availability_violations} rows where availability_timestamp > decision_timestamp."
                )

        has_critical_issue = not is_sorted or availability_violations > 0

        return {
            "status": "FAILED" if has_critical_issue else ("WARNING" if issues else "PASSED"),
            "total_observations": n,
            "is_sorted": is_sorted,
            "duplicate_timestamps": duplicates,
            "availability_violations": availability_violations,
            "label_horizon_steps": label_horizon_steps,
            "start_timestamp": str(ts.iloc[0]) if n > 0 else None,
            "end_timestamp": str(ts.iloc[-1]) if n > 0 else None,
            "issues": issues,
        }
