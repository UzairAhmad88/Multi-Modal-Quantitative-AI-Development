"""
Position Limits Constraint for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
from portfolio.constraints.base import BaseConstraint


class PositionConstraint(BaseConstraint):
    """Enforces min and max position bounds per asset."""

    def __init__(self, min_weight: float = 0.0, max_weight: float = 0.20, long_only: bool = True):
        super().__init__("PositionConstraint")
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.long_only = long_only

    def validate(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        for asset, w in weights.items():
            if self.long_only and w < -1e-7:
                return False, f"Asset '{asset}' violates long_only constraint: weight={w:.4f}"
            if w > self.max_weight + 1e-7:
                return False, f"Asset '{asset}' exceeds max_position_weight {self.max_weight}: weight={w:.4f}"
            if not self.long_only and w < self.min_weight - 1e-7:
                return False, f"Asset '{asset}' below min_position_weight {self.min_weight}: weight={w:.4f}"
        return True, "Position limits satisfied"
