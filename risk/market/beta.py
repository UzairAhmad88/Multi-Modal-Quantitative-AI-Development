"""
Portfolio & Asset Beta Calculator for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class BetaCalculator:
    """Calculates Portfolio and Asset Betas relative to a configured benchmark."""

    @staticmethod
    def calculate_beta(
        asset_returns: np.ndarray,
        benchmark_returns: np.ndarray,
    ) -> float:
        """Compute beta: Cov(R_i, R_m) / Var(R_m)."""
        r_i = np.array(asset_returns, dtype=float)
        r_m = np.array(benchmark_returns, dtype=float)

        if len(r_i) != len(r_m) or len(r_m) < 2:
            return 1.0

        var_m = float(np.var(r_m, ddof=1))
        if var_m <= 1e-12:
            return 1.0

        cov_im = float(np.cov(r_i, r_m)[0, 1])
        beta = cov_im / var_m
        return float(beta)

    @staticmethod
    def calculate_portfolio_beta(
        weights: Dict[str, float],
        asset_betas: Dict[str, float],
    ) -> float:
        """Weighted sum of asset betas."""
        port_beta = sum(weights.get(a, 0.0) * asset_betas.get(a, 1.0) for a in weights)
        return float(port_beta)
