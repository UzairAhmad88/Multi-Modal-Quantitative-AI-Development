"""
Signal-Weighted Allocator for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from portfolio.optimization.base import BasePortfolioOptimizer, OptimizerResult
from portfolio.sizing.signal_based import SignalBasedSizer
from portfolio.constraints.engine import ConstraintEngine


class SignalWeightedOptimizer(BasePortfolioOptimizer):
    """Allocates portfolio weights proportional to normalized alpha prediction scores."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("SignalWeightedOptimizer", config)
        self.sizer = SignalBasedSizer(long_only=self.config.get("long_only", True))

    def fit(self, returns: np.ndarray, asset_names: Optional[List[str]] = None) -> "SignalWeightedOptimizer":
        return self

    def optimize(
        self,
        alpha_scores: Optional[Dict[str, float]] = None,
        cov_matrix: Optional[np.ndarray] = None,
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> OptimizerResult:
        if not alpha_scores:
            return OptimizerResult(weights={}, objective_value=0.0, solver_status="FAILED", warnings=["Alpha scores required"])

        weights = self.sizer.calculate_weights(alpha_scores)

        constraint_engine = ConstraintEngine(self.config.get("constraints"))
        eval_res = constraint_engine.evaluate_all(weights, current_weights, asset_metadata)

        solver_status = "OPTIMAL" if eval_res["is_feasible"] else "INFEASIBLE"

        return OptimizerResult(
            weights=weights,
            objective_value=0.0,
            solver_status=solver_status,
            constraint_status=eval_res,
            warnings=eval_res["failed_constraints"],
        )
