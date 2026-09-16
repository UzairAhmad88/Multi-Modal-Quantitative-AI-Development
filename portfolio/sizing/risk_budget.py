"""
Risk-Budget Position Sizer for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
import numpy as np
from portfolio.sizing.base import BasePositionSizer


class RiskBudgetSizer(BasePositionSizer):
    """Sizes positions according to configured asset or sector risk budgets."""

    def __init__(self, risk_budgets: Optional[Dict[str, float]] = None):
        self.risk_budgets = risk_budgets or {}

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

        # Default equal risk budget if none specified
        n = len(assets)
        budgets = {a: self.risk_budgets.get(a, 1.0 / n) for a in assets}

        # Weight_i = Budget_i / Volatility_i
        unnorm_weights = []
        for a in assets:
            b = budgets[a]
            v = vols.get(a, 0.20)
            if v <= 1e-6:
                v = 0.20
            unnorm_weights.append(b / v)

        unnorm_weights = np.array(unnorm_weights, dtype=float)
        total = np.sum(unnorm_weights)
        if total <= 1e-12:
            return {a: 1.0 / n for a in assets}

        weights = unnorm_weights / total
        return {assets[i]: float(weights[i]) for i in range(len(assets))}
