"""
Position Sizing Engine implementing Signal-Based, Volatility-Based, Risk Budgeting, and Fractional Kelly Sizing.
"""

import numpy as np
from typing import Dict, Any, Optional


class PositionSizingEngine:
    """Calculates position sizes based on volatility, risk budgets, or fractional Kelly criterion."""

    @staticmethod
    def calculate_fractional_kelly(
        win_rate: float = 0.55,
        win_loss_ratio: float = 1.5,
        fraction: float = 0.25
    ) -> float:
        """Calculates fractional Kelly position fraction: f* = (p(b+1) - 1) / b * fraction."""
        p = win_rate
        q = 1.0 - p
        b = win_loss_ratio
        if b <= 0:
            return 0.0
        full_kelly = (p * b - q) / b
        full_kelly = max(0.0, full_kelly)
        return float(round(full_kelly * fraction, 4))

    @staticmethod
    def calculate_volatility_sized_weights(
        signals: Dict[str, float],
        volatilities: Dict[str, float],
        target_risk_per_asset: float = 0.02
    ) -> Dict[str, float]:
        """Sizes positions such that each asset contributes approximately target_risk_per_asset."""
        if not signals:
            return {}
        weights = {}
        for asset, sig in signals.items():
            vol = volatilities.get(asset, 0.20)
            vol = max(vol, 0.05)
            w = (target_risk_per_asset / vol) * np.sign(sig)
            weights[asset] = float(w)
        total = sum(abs(v) for v in weights.values())
        if total > 1.0:
            weights = {k: v / total for k, v in weights.items()}
        return weights
