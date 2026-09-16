"""
Data Quality Validator for Quantitative Research.
Validates price sanity, volume bounds, missing rates, timestamp continuity, and schema integrity.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np


class DataQualityValidator:
    """Audits data quality and price relationship integrity."""

    @staticmethod
    def validate_ohlcv_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        issues: List[str] = []
        required_cols = {"open", "high", "low", "close", "volume"}
        current_cols = set(c.lower() for c in df.columns)

        if not required_cols.issubset(current_cols):
            missing = required_cols - current_cols
            issues.append(f"Schema Mismatch: Missing required columns {missing}")
            return {"status": "FAILED", "issues": issues, "passed": False}

        # Normalize column names for check
        d = {c.lower(): c for c in df.columns}
        high = df[d["high"]]
        low = df[d["low"]]
        open_p = df[d["open"]]
        close_p = df[d["close"]]
        vol = df[d["volume"]]

        # Check 1: High >= max(Open, Close, Low)
        max_oc = np.maximum(open_p, close_p)
        invalid_high = (high < max_oc) | (high < low)
        high_violations = int(np.sum(invalid_high))
        if high_violations > 0:
            issues.append(f"Price Sanity Violation: High price is less than Open/Close/Low in {high_violations} rows.")

        # Check 2: Low <= min(Open, Close, High)
        min_oc = np.minimum(open_p, close_p)
        invalid_low = (low > min_oc) | (low > high)
        low_violations = int(np.sum(invalid_low))
        if low_violations > 0:
            issues.append(f"Price Sanity Violation: Low price is greater than Open/Close/High in {low_violations} rows.")

        # Check 3: Negative volume
        neg_vol = int(np.sum(vol < 0))
        if neg_vol > 0:
            issues.append(f"Volume Violation: Negative volume detected in {neg_vol} rows.")

        # Check 4: Missing values
        missing_count = int(df.isna().sum().sum())
        if missing_count > 0:
            issues.append(f"Missing Values: Total missing entries = {missing_count}.")

        # Check 5: Duplicate timestamps
        if "date" in d or "timestamp" in d:
            time_col = d.get("date") or d.get("timestamp")
            dups = int(df[time_col].duplicated().sum())
            if dups > 0:
                issues.append(f"Timestamp Continuity: {dups} duplicate timestamp entries found.")

        passed = len(issues) == 0
        return {
            "status": "PASSED" if passed else "WARNING",
            "passed": passed,
            "total_rows": len(df),
            "high_violations": high_violations,
            "low_violations": low_violations,
            "negative_volume_rows": neg_vol,
            "missing_entries": missing_count,
            "issues": issues,
        }
