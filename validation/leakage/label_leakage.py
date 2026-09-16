"""
Target Label Correlation & Indirect Leakage Auditor for Walk-Forward OS.
Detects features that contain direct or derivative target information.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class LabelLeakageAuditor:
    """Audits feature matrix against target labels for artificial high correlation and direct target leakage."""

    @staticmethod
    def audit_label_leakage(
        df: pd.DataFrame,
        target_col: str = "target",
        correlation_threshold: float = 0.95,
    ) -> Dict[str, Any]:
        issues = []
        suspicious_features = []

        if target_col not in df.columns:
            return {"status": "SKIPPED", "reason": f"Target column '{target_col}' missing"}

        target = df[target_col].fillna(0)
        num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != target_col]

        for col in num_cols:
            series = df[col].fillna(0)
            if series.std() == 0 or target.std() == 0:
                continue
            corr = float(np.abs(np.corrcoef(series, target)[0, 1]))
            if corr >= correlation_threshold:
                suspicious_features.append({"feature": col, "correlation": round(corr, 4)})
                issues.append(f"LABEL_LEAKAGE: Feature '{col}' exhibits near-perfect correlation ({corr:.4f}) with target '{target_col}'.")

        has_leakage = len(suspicious_features) > 0
        return {
            "status": "FAILED" if has_leakage else "PASSED",
            "has_label_leakage": has_leakage,
            "correlation_threshold": correlation_threshold,
            "suspicious_features": suspicious_features,
            "issues": issues,
        }
