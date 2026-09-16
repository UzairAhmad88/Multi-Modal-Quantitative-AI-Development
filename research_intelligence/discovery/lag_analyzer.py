"""
Lag Analyzer for Quantitative Lead-Lag Relationship Exploration.
Evaluates cross-correlations across configurable temporal lags (t, t+1, t+5, t+10, t+20).
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats


class LagAnalyzer:
    """Analyzes predictive lead-lag relationships across specified time horizons."""

    def __init__(self, lags: List[int] = [0, 1, 5, 10, 20]):
        self.lags = lags

    def analyze_lags(
        self,
        df: pd.DataFrame,
        feature_col: str,
        target_col: str
    ) -> Dict[str, Any]:
        """Calculates correlations between feature at time t and target at time t + lag."""
        if df.empty or feature_col not in df.columns or target_col not in df.columns:
            return {"status": "INVALID_INPUT", "lag_results": []}

        lag_results = []
        for lag in self.lags:
            if lag == 0:
                s_feat = df[feature_col]
                s_targ = df[target_col]
            else:
                s_feat = df[feature_col]
                s_targ = df[target_col].shift(-lag)

            valid = pd.DataFrame({"x": s_feat, "y": s_targ}).dropna()
            if len(valid) < 10:
                continue

            corr, p_val = stats.pearsonr(valid["x"], valid["y"])
            spearman_corr, s_pval = stats.spearmanr(valid["x"], valid["y"])

            lag_results.append({
                "lag": lag,
                "horizon": f"t+{lag}",
                "pearson_corr": round(float(corr), 4),
                "pearson_pvalue": round(float(p_val), 6),
                "spearman_corr": round(float(spearman_corr), 4),
                "spearman_pvalue": round(float(s_pval), 6),
                "n_obs": len(valid)
            })

        # Identify optimal lag with highest absolute correlation
        optimal_lag = max(lag_results, key=lambda r: abs(r["pearson_corr"])) if lag_results else None

        return {
            "status": "SUCCESS",
            "feature": feature_col,
            "target": target_col,
            "optimal_lag": optimal_lag,
            "lag_results": lag_results
        }
