"""
Uncertainty Estimation & Calibration Module
Calculates prediction uncertainty bounds, ensemble model dispersion, and confidence calibration reliability curves.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd


class UncertaintyAnalyzer:
    """Quantitative Prediction Uncertainty & Reliability Calibration Engine."""

    def __init__(self, predictions_df: pd.DataFrame):
        """
        Initialize UncertaintyAnalyzer.
        :param predictions_df: DataFrame containing model prediction columns and ground truth target.
        """
        self.df = predictions_df.copy()

    def compute_ensemble_uncertainty(
        self, model_cols: List[str]
    ) -> pd.DataFrame:
        """
        Calculate ensemble mean prediction, variance, and standard deviation (disagreement index).
        """
        df = self.df.copy()
        existing_cols = [c for c in model_cols if c in df.columns]

        if not existing_cols:
            df["ensemble_mean"] = 0.0
            df["ensemble_variance"] = 0.0
            df["disagreement_index"] = 0.0
            return df

        df["ensemble_mean"] = df[existing_cols].mean(axis=1)
        df["ensemble_variance"] = df[existing_cols].var(axis=1).fillna(0.0)
        df["disagreement_index"] = np.sqrt(df["ensemble_variance"])

        # 95% Confidence Interval bounds (assuming normal distribution)
        df["ci_lower_95"] = df["ensemble_mean"] - 1.96 * df["disagreement_index"]
        df["ci_upper_95"] = df["ensemble_mean"] + 1.96 * df["disagreement_index"]

        return df

    def compute_reliability_calibration(
        self,
        prob_col: str = "predicted_prob",
        target_col: str = "realized_direction",
        bins: int = 5,
    ) -> pd.DataFrame:
        """
        Compute confidence calibration curve comparing predicted confidence buckets against realized outcome frequency.
        """
        df = self.df.dropna(subset=[prob_col, target_col]).copy()
        if len(df) == 0:
            return pd.DataFrame()

        bin_edges = np.linspace(0.0, 1.0, bins + 1)
        df["bin"] = pd.cut(df[prob_col], bins=bin_edges, include_lowest=True, labels=False)

        calibration_stats = []
        for b in range(bins):
            sub = df[df["bin"] == b]
            if len(sub) == 0:
                mean_pred = (bin_edges[b] + bin_edges[b + 1]) / 2.0
                obs_freq = 0.0
                count = 0
            else:
                mean_pred = float(sub[prob_col].mean())
                obs_freq = float(sub[target_col].mean())
                count = int(len(sub))

            calibration_stats.append({
                "bin_idx": b,
                "bin_range": f"{int(bin_edges[b]*100)}-{int(bin_edges[b+1]*100)}%",
                "mean_predicted_confidence": round(mean_pred, 4),
                "observed_frequency": round(obs_freq, 4),
                "calibration_error": round(abs(mean_pred - obs_freq), 4),
                "sample_count": count,
            })

        return pd.DataFrame(calibration_stats)

    def compute_conformal_bounds(
        self, pred_col: str, target_col: str, alpha: float = 0.10
    ) -> Dict[str, float]:
        """
        Compute split conformal prediction coverage bounds (1 - alpha coverage).
        """
        df = self.df.dropna(subset=[pred_col, target_col]).copy()
        if len(df) < 10:
            return {"q_hat": 0.05, "target_coverage": 1.0 - alpha, "empirical_coverage": 1.0}

        residuals = np.abs(df[target_col] - df[pred_col])
        q_level = np.ceil((len(residuals) + 1) * (1 - alpha)) / len(residuals)
        q_level = min(1.0, max(0.0, q_level))
        q_hat = float(np.quantile(residuals, q_level))

        in_bounds = (residuals <= q_hat).mean()

        return {
            "q_hat": round(q_hat, 4),
            "target_coverage": round(1.0 - alpha, 4),
            "empirical_coverage": round(float(in_bounds), 4),
        }
