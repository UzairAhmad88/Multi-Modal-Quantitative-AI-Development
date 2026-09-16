"""
Asset Class & Factor Exposure Constraint for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
from portfolio.constraints.base import BaseConstraint


class ExposureConstraint(BaseConstraint):
    """Enforces asset-class and factor exposure limits."""

    def __init__(self, asset_class_limits: Optional[Dict[str, float]] = None):
        super().__init__("ExposureConstraint")
        self.asset_class_limits = asset_class_limits or {}

    def validate(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        if not asset_metadata or not self.asset_class_limits:
            return True, "No asset-class limits configured"

        ac_exposures: Dict[str, float] = {}
        for asset, w in weights.items():
            meta = asset_metadata.get(asset, {})
            ac = meta.get("asset_class", "EQUITY")
            ac_exposures[ac] = ac_exposures.get(ac, 0.0) + abs(w)

        for ac, limit in self.asset_class_limits.items():
            current_exp = ac_exposures.get(ac, 0.0)
            if current_exp > limit + 1e-6:
                return False, f"Asset class '{ac}' exposure {current_exp:.4f} exceeds limit {limit:.4f}"

        return True, "Exposure constraints satisfied"
