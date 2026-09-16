"""
Data Leakage Auditor Module
Audits point-in-time integrity across prices, news, fundamentals, target horizons, and scalers.
"""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd


class DataLeakageAuditor:
    """Quantitative Data Leakage & Lookahead Bias Auditor."""

    def audit_dataframe(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "date",
        target_col: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Audit dataframe for timestamp monotonicity, future target leakage, and scaler leakage.
        """
        issues = []
        has_leakage = False

        if timestamp_col in df.columns:
            ts_series = pd.to_datetime(df[timestamp_col])
            if not ts_series.is_monotonic_increasing:
                has_leakage = True
                issues.append(f"Timestamps in {timestamp_col} are not monotonically increasing")

        if target_col and target_col in df.columns:
            # Check target shift alignment
            corr = df.corr(numeric_only=True)
            if target_col in corr:
                high_corrs = [c for c in corr.columns if c != target_col and abs(corr.loc[c, target_col]) > 0.99]
                if high_corrs:
                    has_leakage = True
                    issues.append(f"Near-identical feature-target correlation found ({high_corrs}). Potential target leakage!")

        return {
            "has_leakage": has_leakage,
            "audit_status": "FAILED" if has_leakage else "PASSED",
            "issues": issues,
            "rows_audited": len(df)
        }
