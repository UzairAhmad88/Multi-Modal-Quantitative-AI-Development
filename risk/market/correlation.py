"""
Correlation Diagnostics & Instability Analyzer for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd


class CorrelationAnalyzer:
    """Computes correlation matrices, rolling correlation, and structural correlation shifts."""

    @staticmethod
    def compute_correlation_matrix(returns_matrix: np.ndarray, asset_names: Optional[List[str]] = None) -> Dict[str, Any]:
        rets = np.array(returns_matrix, dtype=float)
        corr = np.corrcoef(rets, rowvar=False)
        if corr.ndim == 0:
            corr = np.array([[float(corr)]])
        corr = np.nan_to_num(corr, nan=1.0)
        corr = np.clip(corr, -1.0, 1.0)

        n = corr.shape[0]
        names = asset_names or [f"Asset_{i}" for i in range(n)]

        if n > 1:
            upper_tri = corr[np.triu_indices(n, k=1)]
            avg_corr = float(np.mean(upper_tri))
            max_corr = float(np.max(upper_tri))
            min_corr = float(np.min(upper_tri))
        else:
            avg_corr, max_corr, min_corr = 1.0, 1.0, 1.0

        # High correlation pairs (> 0.75)
        high_corr_pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                val = float(corr[i, j])
                if abs(val) >= 0.75:
                    high_corr_pairs.append({
                        "asset_1": names[i],
                        "asset_2": names[j],
                        "correlation": val,
                    })

        return {
            "avg_correlation": avg_corr,
            "max_correlation": max_corr,
            "min_correlation": min_corr,
            "high_correlation_pairs": high_corr_pairs,
            "correlation_matrix": corr.tolist(),
        }

    @staticmethod
    def detect_correlation_instability(
        returns_period_1: np.ndarray,
        returns_period_2: np.ndarray,
    ) -> Dict[str, Any]:
        """Detect structural shifts between two historical correlation matrices."""
        c1 = np.corrcoef(returns_period_1, rowvar=False)
        c2 = np.corrcoef(returns_period_2, rowvar=False)

        diff = np.abs(c1 - c2)
        mean_diff = float(np.mean(diff))
        max_diff = float(np.max(diff))

        return {
            "correlation_change_mean": mean_diff,
            "correlation_change_max": max_diff,
            "is_unstable": mean_diff > 0.25,
            "status": "HIGH_INSTABILITY" if mean_diff > 0.25 else "STABLE",
        }
