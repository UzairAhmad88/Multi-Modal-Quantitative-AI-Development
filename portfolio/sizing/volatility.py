"""
Volatility-Based Position Sizer & Volatility Targeting for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
from portfolio.sizing.base import BasePositionSizer


class VolatilitySizer(BasePositionSizer):
    """Sizes positions inverse to asset volatility and scales portfolio to target volatility."""

    def __init__(self, target_volatility: Optional[float] = 0.12, annualization: int = 252):
        self.target_volatility = target_volatility
        self.annualization = annualization

    def calculate_weights(
        self,
        alpha_scores: Dict[str, float],
        volatilities: Optional[Dict[str, float]] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
        target_volatility: Optional[float] = None,
    ) -> Dict[str, float]:
        if not alpha_scores:
            return {}

        assets = list(alpha_scores.keys())
        vols = volatilities or {}

        inv_vols = []
        for a in assets:
            v = vols.get(a, 0.20)  # Default 20% annual vol fallback
            if v <= 1e-6:
                v = 0.20
            inv_vols.append(1.0 / v)

        inv_vols = np.array(inv_vols, dtype=float)
        total = np.sum(inv_vols)
        if total <= 1e-12:
            n = len(assets)
            return {a: 1.0 / n for a in assets}

        raw_weights = inv_vols / total
        return {assets[i]: float(raw_weights[i]) for i in range(len(assets))}

    def apply_volatility_targeting(
        self,
        weights: Dict[str, float],
        portfolio_volatility: float,
        target_volatility: Optional[float] = None,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Scale portfolio exposure toward the target volatility."""
        target_vol = target_volatility or self.target_volatility or 0.12
        if portfolio_volatility <= 1e-6:
            scaling_factor = 1.0
        else:
            scaling_factor = float(target_vol / portfolio_volatility)
            scaling_factor = min(scaling_factor, 2.0)  # Cap max leverage scaling at 2.0x

        scaled_weights = {a: w * scaling_factor for a, w in weights.items()}
        diagnostics = {
            "realized_volatility": float(portfolio_volatility),
            "target_volatility": float(target_vol),
            "scaling_factor": float(scaling_factor),
        }
        return scaled_weights, diagnostics
