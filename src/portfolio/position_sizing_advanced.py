"""
Advanced Position Sizing Module
Provides volatility targeting, confidence-adjusted sizing, and alpha-strength position scaling.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd


class VolatilityTargetingEngine:
    """Quantitative Volatility Targeting Engine."""

    def __init__(self, target_volatility_ann: float = 0.15, max_leverage: float = 1.0):
        self.target_volatility = target_volatility_ann
        self.max_leverage = max_leverage

    def scale_portfolio(
        self, weights: pd.Series, covariance: pd.DataFrame
    ) -> Tuple[pd.Series, float]:
        """
        Scale portfolio weights to hit target annualized volatility.
        Returns (scaled_weights, leverage_multiplier).
        """
        w = weights.values.reshape(-1, 1)
        cov = covariance.values

        port_var = float((w.T @ cov @ w).item())
        current_vol = np.sqrt(max(1e-8, port_var))

        if current_vol < 1e-6:
            return weights, 1.0

        multiplier = min(self.max_leverage, self.target_volatility / current_vol)
        scaled_w = weights * multiplier

        return scaled_w.round(6), round(float(multiplier), 4)


class ConfidencePositionSizer:
    """Confidence-Adjusted Position Sizing Engine."""

    def size_positions(
        self, weights: pd.Series, confidence_scores: Dict[str, float]
    ) -> pd.Series:
        """
        Scale weights by model prediction confidence scores.
        """
        conf_series = pd.Series([confidence_scores.get(s, 0.50) for s in weights.index], index=weights.index)
        adj_w = weights * conf_series
        total = adj_w.sum()
        if total > 0:
            adj_w = adj_w / total
        return adj_w.round(6)
