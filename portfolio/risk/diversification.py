"""
Diversification & Correlation Diagnostics for Portfolio Construction OS.
"""

from typing import Dict, Any, Tuple
import numpy as np


class DiversificationAnalyzer:
    """Calculates Portfolio Diversification Ratio, correlation matrix metrics, and asset clusters."""

    @staticmethod
    def calculate_diversification_ratio(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        w = np.array(weights, dtype=float)
        cov = np.array(cov_matrix, dtype=float)

        vols = np.sqrt(np.maximum(1e-12, np.diag(cov)))
        weighted_vol_sum = float(np.sum(abs(w) * vols))

        port_var = float(w.T @ cov @ w)
        port_vol = np.sqrt(max(1e-12, port_var))

        if port_vol <= 1e-12:
            return 1.0

        div_ratio = weighted_vol_sum / port_vol
        return float(div_ratio)

    @staticmethod
    def analyze_correlation(cov_matrix: np.ndarray) -> Dict[str, Any]:
        cov = np.array(cov_matrix, dtype=float)
        vols = np.sqrt(np.maximum(1e-12, np.diag(cov)))
        outer_vols = np.outer(vols, vols)
        corr = cov / outer_vols
        corr = np.clip(corr, -1.0, 1.0)

        n = corr.shape[0]
        if n > 1:
            upper_tri = corr[np.triu_indices(n, k=1)]
            avg_corr = float(np.mean(upper_tri))
            max_corr = float(np.max(upper_tri))
            min_corr = float(np.min(upper_tri))
        else:
            avg_corr = 1.0
            max_corr = 1.0
            min_corr = 1.0

        return {
            "avg_correlation": avg_corr,
            "max_correlation": max_corr,
            "min_correlation": min_corr,
            "correlation_matrix": corr.tolist(),
        }
