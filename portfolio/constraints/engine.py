"""
Central Constraint Engine Facade for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional, Tuple
from portfolio.constraints.base import BaseConstraint
from portfolio.constraints.position import PositionConstraint
from portfolio.constraints.sector import SectorConstraint
from portfolio.constraints.exposure import ExposureConstraint
from portfolio.constraints.turnover import TurnoverConstraint
from portfolio.constraints.leverage import LeverageConstraint
from portfolio.constraints.liquidity import LiquidityConstraint


class ConstraintEngine:
    """Evaluates all portfolio constraints and returns detailed validation diagnostics."""

    def __init__(self, constraints_config: Optional[Dict[str, Any]] = None):
        self.config = constraints_config or {}
        self.constraints: List[BaseConstraint] = []

        long_only = self.config.get("long_only", True)
        min_w = self.config.get("min_position_weight", 0.0)
        max_w = self.config.get("max_position_weight", 1.0)
        self.constraints.append(PositionConstraint(min_weight=min_w, max_weight=max_w, long_only=long_only))

        sector_limits = self.config.get("sector_limits", {})
        if sector_limits:
            self.constraints.append(SectorConstraint(sector_limits))

        ac_limits = self.config.get("asset_class_limits", {})
        if ac_limits:
            self.constraints.append(ExposureConstraint(ac_limits))

        max_turnover = self.config.get("max_turnover", 0.50)
        self.constraints.append(TurnoverConstraint(max_turnover=max_turnover))

        max_lev = self.config.get("max_leverage", 1.0)
        self.constraints.append(LeverageConstraint(max_leverage=max_lev))

        max_adv = self.config.get("max_adv_participation", 0.10)
        port_val = self.config.get("portfolio_value", 100000.0)
        self.constraints.append(LiquidityConstraint(max_adv_participation=max_adv, portfolio_value=port_val))

    def evaluate_all(
        self,
        target_weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Evaluate target weights against all registered constraints."""
        all_passed = True
        failed_constraints: List[str] = []
        constraint_details: Dict[str, Dict[str, Any]] = {}

        for constraint in self.constraints:
            passed, msg = constraint.validate(
                weights=target_weights,
                current_weights=current_weights,
                asset_metadata=asset_metadata,
            )
            constraint_details[constraint.name] = {"passed": passed, "message": msg}
            if not passed:
                all_passed = False
                failed_constraints.append(f"{constraint.name}: {msg}")

        return {
            "status": "PASSED" if all_passed else "INFEASIBLE",
            "is_feasible": all_passed,
            "failed_constraints": failed_constraints,
            "details": constraint_details,
        }
