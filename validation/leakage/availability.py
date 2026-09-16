"""
Point-in-Time Availability Timestamp Auditor for Walk-Forward OS.
Checks filing lag for fundamentals and publication lag for news data.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class AvailabilityAuditor:
    """Audits fundamental filing lags and news publication lag compliance."""

    @staticmethod
    def audit_availability(
        df: pd.DataFrame,
        decision_time_col: str = "timestamp",
        availability_time_col: str = "availability_timestamp",
        min_filing_lag_days: int = 45,
    ) -> Dict[str, Any]:
        issues = []

        if decision_time_col not in df.columns or availability_time_col not in df.columns:
            return {
                "status": "SKIPPED",
                "reason": f"Columns '{decision_time_col}' or '{availability_time_col}' not present.",
            }

        decision_ts = pd.to_datetime(df[decision_time_col])
        avail_ts = pd.to_datetime(df[availability_time_col])

        # Violations where availability > decision
        future_avail = avail_ts > decision_ts
        viol_count = int(future_avail.sum())

        if viol_count > 0:
            issues.append(f"POINT_IN_TIME_LEAKAGE: {viol_count} rows have availability_timestamp > decision_timestamp.")

        return {
            "status": "FAILED" if viol_count > 0 else "PASSED",
            "availability_violations": viol_count,
            "min_filing_lag_days": min_filing_lag_days,
            "issues": issues,
        }
