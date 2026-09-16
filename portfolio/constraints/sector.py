"""
Sector Limits Constraint for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
from portfolio.constraints.base import BaseConstraint


class SectorConstraint(BaseConstraint):
    """Enforces maximum exposure limits per sector."""

    def __init__(self, sector_limits: Dict[str, float]):
        super().__init__("SectorConstraint")
        self.sector_limits = sector_limits

    def validate(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        if not asset_metadata or not self.sector_limits:
            return True, "No sector metadata or limits configured"

        sector_exposures: Dict[str, float] = {}
        for asset, w in weights.items():
            meta = asset_metadata.get(asset, {})
            sec = meta.get("sector", "Unassigned")
            sector_exposures[sec] = sector_exposures.get(sec, 0.0) + abs(w)

        for sec, limit in self.sector_limits.items():
            current_exp = sector_exposures.get(sec, 0.0)
            if current_exp > limit + 1e-6:
                return False, f"Sector '{sec}' exposure {current_exp:.4f} exceeds limit {limit:.4f}"

        return True, "Sector constraints satisfied"
