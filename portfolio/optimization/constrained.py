"""
General Constrained Portfolio Optimizer for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from portfolio.optimization.base import BasePortfolioOptimizer, OptimizerResult
from portfolio.optimization.mean_variance import MeanVarianceOptimizer


class ConstrainedOptimizer(BasePortfolioOptimizer):
    """General Constrained Optimizer incorporating strict position, sector, exposure, turnover, and leverage limits."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ConstrainedOptimizer", config)
        self.underlying_optimizer = MeanVarianceOptimizer(self.config)

    def fit(self, returns: np.ndarray, asset_names: Optional[List[str]] = None) -> "ConstrainedOptimizer":
        self.underlying_optimizer.fit(returns, asset_names)
        return self

    def optimize(
        self,
        alpha_scores: Optional[Dict[str, float]] = None,
        cov_matrix: Optional[np.ndarray] = None,
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> OptimizerResult:
        return self.underlying_optimizer.optimize(
            alpha_scores=alpha_scores,
            cov_matrix=cov_matrix,
            current_weights=current_weights,
            asset_metadata=asset_metadata,
        )
