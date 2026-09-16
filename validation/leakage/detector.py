"""
Comprehensive Leakage Detector Engine for Walk-Forward OS.
Unified auditor conducting 6-stage data leakage checks across dataset features, preprocessing, and timelines.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from validation.leakage.feature_leakage import FeatureLeakageAuditor
from validation.leakage.label_leakage import LabelLeakageAuditor
from validation.leakage.temporal_leakage import TemporalLeakageAuditor
from validation.leakage.availability import AvailabilityAuditor


class LeakageDetector:
    """Master audit engine executing complete data leakage diagnostics."""

    @staticmethod
    def audit_full_dataset(
        df: pd.DataFrame,
        decision_col: str = "timestamp",
        target_col: Optional[str] = "target",
        availability_col: Optional[str] = "availability_timestamp",
        train_means: Optional[np.ndarray] = None,
        train_stds: Optional[np.ndarray] = None,
        full_means: Optional[np.ndarray] = None,
        full_stds: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        issues: List[str] = []

        # 1. Feature publication timestamp leakage
        feat_res = FeatureLeakageAuditor.audit_feature_timestamps(df, decision_col=decision_col)
        if feat_res.get("issues"):
            issues.extend(feat_res["issues"])

        # 2. Label correlation leakage
        label_res = {}
        if target_col and target_col in df.columns:
            label_res = LabelLeakageAuditor.audit_label_leakage(df, target_col=target_col)
            if label_res.get("issues"):
                issues.extend(label_res["issues"])

        # 3. Availability timestamp leakage
        avail_res = {}
        if availability_col and availability_col in df.columns:
            avail_res = AvailabilityAuditor.audit_availability(df, decision_time_col=decision_col, availability_time_col=availability_col)
            if avail_res.get("issues"):
                issues.extend(avail_res["issues"])

        # 4. Preprocessing scaler leakage
        scaler_res = LeakageDetector.audit_scaler_leakage(train_means, train_stds, full_means, full_stds)
        if scaler_res.get("issues"):
            issues.extend(scaler_res["issues"])

        has_leakage = len(issues) > 0

        return {
            "status": "LEAKAGE_DETECTED" if has_leakage else "CLEAN",
            "has_leakage": has_leakage,
            "total_issues": len(issues),
            "feature_leakage_result": feat_res,
            "label_leakage_result": label_res,
            "availability_result": avail_res,
            "scaler_leakage_result": scaler_res,
            "issues": issues,
        }

    @staticmethod
    def audit_scaler_leakage(
        train_means: Optional[np.ndarray],
        train_stds: Optional[np.ndarray],
        full_means: Optional[np.ndarray],
        full_stds: Optional[np.ndarray],
        tolerance: float = 1e-4,
    ) -> Dict[str, Any]:
        """Audits whether scalers were fitted on the full dataset instead of train set only."""
        if train_means is None or full_means is None or train_stds is None or full_stds is None:
            return {"status": "SKIPPED", "reason": "Scaler parameters not provided"}

        mean_diff = float(np.max(np.abs(train_means - full_means)))
        std_diff = float(np.max(np.abs(train_stds - full_stds)))
        scaler_leakage = bool(mean_diff < tolerance and std_diff < tolerance)

        issues = []
        if scaler_leakage:
            issues.append("PREPROCESSING_LEAKAGE: Scaler parameters appear fitted on full dataset prior to train/test split.")

        return {
            "status": "FAILED" if scaler_leakage else "PASSED",
            "scaler_leakage": scaler_leakage,
            "max_mean_difference": mean_diff,
            "max_std_difference": std_diff,
            "issues": issues,
        }
