"""
Performance & Feature Importance Stability Engine for Walk-Forward OS.
Analyzes cross-fold performance dispersion and feature rank stability across walk-forward windows.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class StabilityAnalyzer:
    """Evaluates stability of model performance and feature importance across temporal folds."""

    @staticmethod
    def evaluate_performance_stability(fold_sharpes: List[float]) -> Dict[str, Any]:
        """Calculates performance dispersion and positive fold ratio."""
        if not fold_sharpes:
            return {"stability_score": 0.0, "status": "NO_DATA"}

        arr = np.array(fold_sharpes, dtype=float)
        mean_s = float(np.mean(arr))
        std_s = float(np.std(arr))
        cv = float(std_s / abs(mean_s)) if abs(mean_s) > 1e-8 else 999.0
        pos_ratio = float(np.mean(arr > 0))

        # Stability score between 0.0 and 1.0
        stability_score = max(0.0, min(1.0, float(pos_ratio * (1.0 / (1.0 + cv)))))

        return {
            "mean_sharpe": round(mean_s, 2),
            "std_sharpe": round(std_s, 2),
            "coefficient_of_variation": round(cv, 2),
            "positive_fold_ratio": round(pos_ratio, 2),
            "stability_score": round(stability_score, 2),
            "status": "HIGH_STABILITY" if stability_score >= 0.65 else ("MODERATE" if stability_score >= 0.45 else "UNSTABLE"),
        }

    @staticmethod
    def evaluate_feature_rank_stability(feature_importance_history: List[Dict[str, float]]) -> Dict[str, Any]:
        """Calculates rank correlation and persistence of top features across walk-forward folds."""
        if not feature_importance_history or len(feature_importance_history) < 2:
            return {"rank_stability_score": 1.0, "status": "INSUFFICIENT_FOLDS"}

        # Collect all feature names
        features = list(feature_importance_history[0].keys())
        ranks = []

        for imp_dict in feature_importance_history:
            s = pd.Series(imp_dict).rank(ascending=False)
            ranks.append(s)

        rank_df = pd.DataFrame(ranks)
        avg_std_rank = float(rank_df.std(axis=0).mean())
        rank_stability = float(max(0.0, 1.0 - (avg_std_rank / max(1, len(features)))))

        return {
            "num_folds": len(feature_importance_history),
            "avg_rank_std": round(avg_std_rank, 2),
            "rank_stability_score": round(rank_stability, 2),
            "status": "STABLE_FEATURES" if rank_stability >= 0.70 else "SHIFTING_FEATURES",
        }
