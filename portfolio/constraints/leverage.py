"""
Leverage and Exposure Constraint for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
from portfolio.constraints.base import BaseConstraint


class LeverageConstraint(BaseConstraint):
    """Enforces gross leverage and net exposure constraints."""

    def __init__(self, max_leverage: float = 1.0, min_net_exposure: float = 0.0, max_net_exposure: float = 1.0):
        super().__init__("LeverageConstraint")
        self.max_leverage = max_leverage
        self.min_net_exposure = min_net_exposure
        self.max_net_exposure = max_net_exposure

    def validate(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        gross = sum(abs(w) for w in weights.values())
        net = sum(w for w in weights.values())

        if gross > self.max_leverage + 1e-6:
            return False, f"Gross exposure {gross:.4f} exceeds max leverage limit {self.max_leverage:.4f}"

        if net > self.max_net_exposure + 1e-6 or net < self.min_net_exposure - 1e-6:
            return False, f"Net exposure {net:.4f} outside range [{self.min_net_exposure}, {self.max_net_exposure}]"

        return True, "Leverage constraint satisfied"
