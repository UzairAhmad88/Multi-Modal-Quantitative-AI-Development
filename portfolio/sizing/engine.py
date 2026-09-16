"""
Position Sizing Engine Facade for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
from portfolio.sizing.signal_based import SignalBasedSizer
from portfolio.sizing.volatility import VolatilitySizer
from portfolio.sizing.risk_budget import RiskBudgetSizer
from portfolio.sizing.confidence_based import ConfidenceBasedSizer


class PositionSizingEngine:
    """Unified engine to calculate raw weights using configured position sizing methods."""

    def __init__(self, sizing_method: str = "signal_based", config: Optional[Dict[str, Any]] = None):
        self.sizing_method = sizing_method
        self.config = config or {}

        if sizing_method == "volatility":
            self.sizer = VolatilitySizer(target_volatility=self.config.get("target_volatility", 0.12))
        elif sizing_method == "risk_budget":
            self.sizer = RiskBudgetSizer(risk_budgets=self.config.get("risk_budgets"))
        elif sizing_method == "confidence_based":
            self.sizer = ConfidenceBasedSizer()
        else:
            long_only = self.config.get("long_only", True)
            self.sizer = SignalBasedSizer(long_only=long_only)

    def size_positions(
        self,
        alpha_scores: Dict[str, float],
        volatilities: Optional[Dict[str, float]] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """Compute unconstrained target weights based on selected sizing method."""
        return self.sizer.calculate_weights(
            alpha_scores=alpha_scores,
            volatilities=volatilities,
            confidence_scores=confidence_scores,
        )
