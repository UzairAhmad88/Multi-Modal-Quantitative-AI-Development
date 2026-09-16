"""
Maximum Diversification Optimizer for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from scipy.optimize import minimize
from portfolio.optimization.base import BasePortfolioOptimizer, OptimizerResult
from portfolio.constraints.engine import ConstraintEngine
from portfolio.utils.covariance import CovarianceEstimator


class MaximumDiversificationOptimizer(BasePortfolioOptimizer):
    """Maximizes the Portfolio Diversification Ratio: (w^T sigma) / sqrt(w^T Sigma w)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("MaximumDiversificationOptimizer", config)
        self.cov_matrix: Optional[np.ndarray] = None
        self.asset_names: List[str] = []

    def fit(self, returns: np.ndarray, asset_names: Optional[List[str]] = None) -> "MaximumDiversificationOptimizer":
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
        vols = np.sqrt(np.maximum(1e-12, np.diag(cov)))
        w0 = np.ones(n) / n

        # Negative diversification ratio to minimize
        def objective(w):
            w = np.array(w)
            weighted_vol = float(w.T @ vols)
            port_vol = np.sqrt(max(1e-12, float(w.T @ cov @ w)))
            div_ratio = weighted_vol / port_vol
            return -div_ratio

        bounds = [(0.0, 1.0) for _ in range(n)]
        cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

        res = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=cons)

        if not res.success:
            return OptimizerResult(
                weights={assets[i]: float(w0[i]) for i in range(n)},
                objective_value=float(-objective(w0)),
                solver_status="FAILED",
                warnings=[f"Max Diversification solver failed: {res.message}"],
            )

        weights = {assets[i]: float(max(0.0, res.x[i])) for i in range(n)}
        tot = sum(weights.values())
        if tot > 0:
            weights = {a: w / tot for a, w in weights.items()}

        constraint_engine = ConstraintEngine(self.config.get("constraints", self.config))
        eval_res = constraint_engine.evaluate_all(weights, current_weights, asset_metadata)

        solver_status = "OPTIMAL" if res.success and eval_res["is_feasible"] else "FEASIBLE"

        return OptimizerResult(
            weights=weights,
            objective_value=float(-res.fun),
            solver_status=solver_status,
            constraint_status=eval_res,
            warnings=eval_res["failed_constraints"],
        )
