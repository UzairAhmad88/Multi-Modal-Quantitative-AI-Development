"""
Equal-Weight Portfolio Optimizer for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from portfolio.optimization.base import BasePortfolioOptimizer, OptimizerResult
from portfolio.constraints.engine import ConstraintEngine


class EqualWeightOptimizer(BasePortfolioOptimizer):
    """Assigns equal weights (1 / N) to all eligible portfolio assets."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("EqualWeightOptimizer", config)
        self.asset_names: List[str] = []

    def fit(self, returns: np.ndarray, asset_names: Optional[List[str]] = None) -> "EqualWeightOptimizer":
        n = returns.shape[1] if returns.ndim > 1 else 1
        self.asset_names = asset_names or [f"Asset_{i}" for i in range(n)]
        return self

    def optimize(
        self,
        alpha_scores: Optional[Dict[str, float]] = None,
        cov_matrix: Optional[np.ndarray] = None,
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> OptimizerResult:
        assets = list(alpha_scores.keys()) if alpha_scores else self.asset_names
        if not assets:
            return OptimizerResult(weights={}, objective_value=0.0, solver_status="FAILED", warnings=["No assets provided"])

        n = len(assets)
        w_val = 1.0 / n
        weights = {a: float(w_val) for a in assets}

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
