"""
Error Analysis & Data/Concept Drift Module
Evaluates model failure modes, directional classification errors, Population Stability Index (PSI),
and Kolmogorov-Smirnov (KS) drift metrics.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


class ErrorAnalyzer:
    """Quantitative Error Analysis & Data Drift Diagnostics Engine."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize ErrorAnalyzer.
        :param df: DataFrame with predicted returns, realized returns, features, and dates.
        """
        self.df = df.copy()

    def compute_error_metrics(
        self, pred_col: str = "predicted_return", target_col: str = "realized_return"
    ) -> Dict[str, float]:
        """
        Calculate regression and classification error metrics.
        """
        df = self.df.dropna(subset=[pred_col, target_col]).copy()
        if len(df) == 0:
            return {"mae": 0.0, "rmse": 0.0, "directional_accuracy": 0.0, "corr": 0.0}

        pred = df[pred_col].values
        target = df[target_col].values

        mae = float(np.mean(np.abs(pred - target)))
        rmse = float(np.sqrt(np.mean((pred - target) ** 2)))

        correct_direction = np.sign(pred) == np.sign(target)
        dir_acc = float(np.mean(correct_direction))

        if len(pred) > 2 and np.std(pred) > 1e-8 and np.std(target) > 1e-8:
            corr, _ = stats.pearsonr(pred, target)
            corr = float(corr) if not np.isnan(corr) else 0.0
        else:
            corr = 0.0

        # Classification matrix (assuming sign > 0 is Positive signal)
        pred_pos = pred > 0
        target_pos = target > 0

        tp = int(np.sum(pred_pos & target_pos))
        fp = int(np.sum(pred_pos & ~target_pos))
        tn = int(np.sum(~pred_pos & ~target_pos))
        fn = int(np.sum(~pred_pos & target_pos))

        return {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "directional_accuracy": round(dir_acc, 4),
            "correlation": round(corr, 4),
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "precision": round(tp / (tp + fp + 1e-8), 4),
            "recall": round(tp / (tp + fn + 1e-8), 4),
        }

    def analyze_failure_regimes(
        self,
        pred_col: str = "predicted_return",
        target_col: str = "realized_return",
        feature_cols: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Identify features/conditions strongly associated with high absolute prediction error.
        """
        df = self.df.dropna(subset=[pred_col, target_col]).copy()
        if df.empty:
            return pd.DataFrame()

        df["abs_error"] = np.abs(df[pred_col] - df[target_col])
        high_error_cutoff = df["abs_error"].quantile(0.80)
        df["is_high_error"] = df["abs_error"] >= high_error_cutoff

        if feature_cols is None:
            feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in [pred_col, target_col, "abs_error", "is_high_error"]]

        regime_summary = []
        for feat in feature_cols[:10]:  # Evaluate top 10 features
            high_err_mean = df[df["is_high_error"]][feat].mean()
            normal_err_mean = df[~df["is_high_error"]][feat].mean()
            ks_stat, p_val = stats.ks_2samp(df[df["is_high_error"]][feat].dropna(), df[~df["is_high_error"]][feat].dropna())

            regime_summary.append({
                "feature": feat,
                "high_error_mean": round(float(high_err_mean), 4) if not np.isnan(high_err_mean) else 0.0,
                "normal_error_mean": round(float(normal_err_mean), 4) if not np.isnan(normal_err_mean) else 0.0,
                "ks_statistic": round(float(ks_stat), 4) if not np.isnan(ks_stat) else 0.0,
                "p_value": round(float(p_val), 4) if not np.isnan(p_val) else 1.0,
            })

        return pd.DataFrame(regime_summary)

    @staticmethod
    def compute_psi(reference: np.ndarray, target: np.ndarray, num_bins: int = 10) -> float:
        """
        Calculate Population Stability Index (PSI) between reference and target distributions.
        PSI < 0.1: No significant drift
        0.1 <= PSI < 0.2: Moderate drift
        PSI >= 0.2: Significant drift
        """
        ref = reference[~np.isnan(reference)]
        tgt = target[~np.isnan(target)]

        if len(ref) < 10 or len(tgt) < 10:
            return 0.0

        percentiles = np.linspace(0, 100, num_bins + 1)
        bin_edges = np.percentile(ref, percentiles)
        bin_edges[0] = -np.inf
        bin_edges[-1] = np.inf

        ref_counts, _ = np.histogram(ref, bins=bin_edges)
        tgt_counts, _ = np.histogram(tgt, bins=bin_edges)

        ref_pct = ref_counts / (len(ref) + 1e-8)
        tgt_pct = tgt_counts / (len(tgt) + 1e-8)

        # Replace zero percentages to prevent log(0)
        ref_pct = np.where(ref_pct == 0, 1e-4, ref_pct)
        tgt_pct = np.where(tgt_pct == 0, 1e-4, tgt_pct)

        psi_val = np.sum((tgt_pct - ref_pct) * np.log(tgt_pct / ref_pct))
        return float(round(psi_val, 4))
