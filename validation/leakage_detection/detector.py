"""
Leakage Detector for Quantitative AI Models.
Audits datasets, feature pipelines, timestamps, and preprocessing logic for future look-ahead bias,
scaler leakage, news/fundamental availability misalignment, and label leakage.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np


class LeakageDetector:
    """Rigorously audits features and pipelines for future data leakage."""

    @staticmethod
    def audit_timestamps(
        features_df: pd.DataFrame,
        prediction_time_col: str = "prediction_time",
        publication_time_col: Optional[str] = "publication_time",
        availability_time_col: Optional[str] = "availability_time",
    ) -> Dict[str, Any]:
        """Validates that all external news and fundamental timestamps precede or equal prediction time."""
        issues: List[str] = []

        if prediction_time_col not in features_df.columns:
            return {"status": "SKIPPED", "reason": f"Column '{prediction_time_col}' missing"}

        pred_time = pd.to_datetime(features_df[prediction_time_col])

        # Check 1: News publication timing
        if publication_time_col and publication_time_col in features_df.columns:
            pub_time = pd.to_datetime(features_df[publication_time_col])
            future_news = pub_time > pred_time
            news_violations = int(np.sum(future_news))
            if news_violations > 0:
                issues.append(f"POTENTIAL DATA LEAKAGE: Found {news_violations} news articles with publication_time > prediction_time.")

        # Check 2: Fundamental availability timing
        if availability_time_col and availability_time_col in features_df.columns:
            avail_time = pd.to_datetime(features_df[availability_time_col])
            future_fund = avail_time > pred_time
            fund_violations = int(np.sum(future_fund))
            if fund_violations > 0:
                issues.append(f"POTENTIAL DATA LEAKAGE: Found {fund_violations} fundamental statements with availability_time > prediction_time.")

        has_leakage = len(issues) > 0
        return {
            "status": "FAILED" if has_leakage else "PASSED",
            "has_leakage": has_leakage,
            "leakage_alert": "POTENTIAL DATA LEAKAGE DETECTED" if has_leakage else "CLEAN",
            "issues": issues,
        }

    @staticmethod
    def audit_scaler_leakage(
        train_means: np.ndarray,
        train_stds: np.ndarray,
        full_means: np.ndarray,
        full_stds: np.ndarray,
        tolerance: float = 1e-4,
    ) -> Dict[str, Any]:
        """Audits whether scaling parameters were fitted on the full dataset instead of train set only."""
        mean_diff = np.max(np.abs(train_means - full_means))
        std_diff = np.max(np.abs(train_stds - full_stds))

        scaler_leakage = bool(mean_diff < tolerance and std_diff < tolerance)

        issues = []
        if scaler_leakage:
            issues.append("POTENTIAL DATA LEAKAGE: Preprocessing scaler appears to be fitted on full dataset prior to train/test split.")

        return {
            "status": "FAILED" if scaler_leakage else "PASSED",
            "scaler_leakage": scaler_leakage,
            "max_mean_difference": float(mean_diff),
            "max_std_difference": float(std_diff),
            "issues": issues,
        }

    @staticmethod
    def audit_target_label_leakage(
        feature_matrix: pd.DataFrame, target_series: pd.Series, max_correlation_threshold: float = 0.98
    ) -> Dict[str, Any]:
        """Audits whether any feature column has an artificially perfect correlation with target label."""
        suspicious_features = []

        for col in feature_matrix.select_dtypes(include=[np.number]).columns:
            corr = float(np.abs(np.corrcoef(feature_matrix[col].fillna(0), target_series.fillna(0))[0, 1]))
            if corr >= max_correlation_threshold and not np.isnan(corr):
                suspicious_features.append({"feature": col, "correlation": round(corr, 4)})

        has_label_leakage = len(suspicious_features) > 0
        issues = []
        if has_label_leakage:
            issues.append(f"POTENTIAL DATA LEAKAGE: High correlation target leakage detected in features: {[s['feature'] for s in suspicious_features]}.")

        return {
            "status": "FAILED" if has_label_leakage else "PASSED",
            "has_label_leakage": has_label_leakage,
            "suspicious_features": suspicious_features,
            "issues": issues,
        }

    @staticmethod
    def audit_survivorship_bias(asset_universe_count: int, delisted_asset_count: int) -> Dict[str, Any]:
        """Documents survivorship bias assessment."""
        has_delisted = delisted_asset_count > 0
        limitation = "" if has_delisted else "LIMITATION: survivorship bias cannot be fully assessed due to lack of historical delisted asset data."

        return {
            "status": "PASSED" if has_delisted else "WARNING",
            "universe_count": asset_universe_count,
            "delisted_count": delisted_asset_count,
            "survivorship_bias_mitigated": has_delisted,
            "limitation": limitation,
        }
