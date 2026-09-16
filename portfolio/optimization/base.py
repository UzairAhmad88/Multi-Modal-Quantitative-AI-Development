"""
Base Portfolio Optimizer Interface for Portfolio Construction OS.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
import numpy as np


@dataclass
class OptimizerResult:
    weights: Dict[str, float]
    objective_value: float
    solver_status: str  # "OPTIMAL", "FEASIBLE", "FAILED", "INFEASIBLE"
    constraint_status: Dict[str, Any] = field(default_factory=dict)
    risk_metrics: Dict[str, Any] = field(default_factory=dict)
    turnover: float = 0.0
    estimated_cost: float = 0.0
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BasePortfolioOptimizer(ABC):
    """Abstract Base Class for Quantitative Portfolio Optimizers."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def fit(self, returns: np.ndarray, asset_names: Optional[List[str]] = None) -> "BasePortfolioOptimizer":
        """Fit statistical inputs (means, covariances, volatilities)."""
        pass

    @abstractmethod
    def optimize(
        self,
        alpha_scores: Optional[Dict[str, float]] = None,
        cov_matrix: Optional[np.ndarray] = None,
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> OptimizerResult:
        """Run optimization and return OptimizerResult."""
        pass
