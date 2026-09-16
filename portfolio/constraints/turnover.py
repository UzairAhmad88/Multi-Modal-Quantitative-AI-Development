"""
Turnover Constraint Module for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
from portfolio.constraints.base import BaseConstraint


class TurnoverConstraint(BaseConstraint):
    """Enforces maximum one-period portfolio turnover limit."""

    def __init__(self, max_turnover: float = 0.50, convention: str = "full"):
        super().__init__("TurnoverConstraint")
        self.max_turnover = max_turnover
        self.convention = convention  # "full" sum(abs(w_new - w_old)) or "half" 0.5*sum(...)

    def calculate_turnover(self, new_weights: Dict[str, float], old_weights: Dict[str, float]) -> float:
        all_assets = set(new_weights.keys()).union(old_weights.keys())
        diff_sum = sum(abs(new_weights.get(a, 0.0) - old_weights.get(a, 0.0)) for a in all_assets)
        if self.convention == "half":
            return 0.5 * diff_sum
        return diff_sum

    def validate(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        if current_weights is None:
            return True, "No current weights provided for turnover check"

        turnover = self.calculate_turnover(weights, current_weights)
        if turnover > self.max_turnover + 1e-6:
            return False, f"Portfolio turnover {turnover:.4f} exceeds max turnover limit {self.max_turnover:.4f}"

        return True, "Turnover constraint satisfied"
