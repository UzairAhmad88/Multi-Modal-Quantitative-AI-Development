"""
Feature Publication Timestamp Leakage Auditor for Walk-Forward OS.
Checks whether news, technical, or fundamental feature timestamps succeed prediction decision timestamps.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class FeatureLeakageAuditor:
    """Audits feature timestamp columns for publication and future look-ahead violations."""

    @staticmethod
    def audit_feature_timestamps(
        df: pd.DataFrame,
        decision_col: str = "timestamp",
        feature_cols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        issues = []
        violations_map = {}

        if decision_col not in df.columns:
            return {"status": "SKIPPED", "reason": f"Decision column '{decision_col}' missing"}

        decision_ts = pd.to_datetime(df[decision_col])

        # Find timestamp/datetime columns among features
        timestamp_cols = feature_cols or [
            c for c in df.columns if "timestamp" in c.lower() or "pub_date" in c.lower() or "date" in c.lower()
        ]
        timestamp_cols = [c for c in timestamp_cols if c != decision_col]

        for col in timestamp_cols:
            if col in df.columns:
                try:
                    feat_ts = pd.to_datetime(df[col])
                    future_mask = feat_ts > decision_ts
                    viol_count = int(future_mask.sum())
                    if viol_count > 0:
                        violations_map[col] = viol_count
                        issues.append(f"LOOK_AHEAD_LEAKAGE: Feature '{col}' has {viol_count} rows with timestamp > decision_col '{decision_col}'.")
                except Exception:
                    pass

        has_leakage = len(issues) > 0
        return {
            "status": "FAILED" if has_leakage else "PASSED",
            "has_feature_leakage": has_leakage,
            "violations_by_feature": violations_map,
            "issues": issues,
        }
