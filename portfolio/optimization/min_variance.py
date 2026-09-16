"""
Minimum-Variance Portfolio Optimizer for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from scipy.optimize import minimize
from portfolio.optimization.base import BasePortfolioOptimizer, OptimizerResult
from portfolio.constraints.engine import ConstraintEngine
from portfolio.utils.covariance import CovarianceEstimator


class MinimumVarianceOptimizer(BasePortfolioOptimizer):
    """Solves for minimum portfolio variance: min w^T Sigma w subject to constraints."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("MinimumVarianceOptimizer", config)
        self.cov_matrix: Optional[np.ndarray] = None
        self.asset_names: List[str] = []

    def fit(self, returns: np.ndarray, asset_names: Optional[List[str]] = None) -> "MinimumVarianceOptimizer":
        n = returns.shape[1] if returns.ndim > 1 else 1
        self.asset_names = asset_names or [f"Asset_{i}" for i in range(n)]
        self.cov_matrix = CovarianceEstimator.sample_covariance(returns)
        return self

    def optimize(
        self,
        alpha_scores: Optional[Dict[str, float]] = None,
        cov_matrix: Optional[np.ndarray] = None,
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> OptimizerResult:
        cov = cov_matrix if cov_matrix is not None else self.cov_matrix
        assets = list(alpha_scores.keys()) if alpha_scores else self.asset_names

        if cov is None or len(assets) == 0:
            return OptimizerResult(weights={}, objective_value=0.0, solver_status="FAILED", warnings=["Covariance matrix or assets missing"])

        n = len(assets)
        w0 = np.ones(n) / n

        # Bounds
        max_w = self.config.get("max_position_weight", 1.0)
        min_w = 0.0 if self.config.get("long_only", True) else self.config.get("min_position_weight", -0.20)
        bounds = [(min_w, max_w) for _ in range(n)]

        # Sum w_i = 1.0 constraint
        cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

        # Turnover constraint if current_weights available
        if current_weights and "max_turnover" in self.config:
            w_curr = np.array([current_weights.get(a, 0.0) for a in assets])
            max_turnover = self.config["max_turnover"]
            cons.append({"type": "ineq", "fun": lambda w: max_turnover - np.sum(np.abs(w - w_curr))})

        def objective(w):
            return float(w.T @ cov @ w)

        res = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=cons)

        if not res.success:
            return OptimizerResult(
                weights={assets[i]: float(w0[i]) for i in range(n)},
                objective_value=float(w0.T @ cov @ w0),
                solver_status="FAILED",
                warnings=[f"Optimizer failed to converge: {res.message}"],
            )

        weights = {assets[i]: float(max(0.0, res.x[i])) for i in range(n)}
        # Renormalize sum to 1.0
        tot = sum(weights.values())
        if tot > 0:
            weights = {a: w / tot for a, w in weights.items()}

        constraint_engine = ConstraintEngine(self.config.get("constraints", self.config))
        eval_res = constraint_engine.evaluate_all(weights, current_weights, asset_metadata)

        solver_status = "OPTIMAL" if res.success and eval_res["is_feasible"] else "FEASIBLE"

        return OptimizerResult(
            weights=weights,
            objective_value=float(res.fun),
            solver_status=solver_status,
            constraint_status=eval_res,
            warnings=eval_res["failed_constraints"],
        )
