"""
Portfolio Objective Engine for Return, Variance, Sharpe, CVaR, and Composite Objective Calculations.
"""

import numpy as np
from typing import Dict, Any, List, Optional


class ObjectiveEngine:
    """Evaluates optimization objectives and loss functions."""

    @staticmethod
    def calculate_expected_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
        """Portfolio expected return: w^T mu."""
        return float(np.dot(weights, expected_returns))

    @staticmethod
    def calculate_variance(weights: np.ndarray, cov: np.ndarray) -> float:
        """Portfolio variance: w^T Sigma w."""
        return float(weights @ cov @ weights)

    @staticmethod
    def calculate_sharpe(weights: np.ndarray, expected_returns: np.ndarray, cov: np.ndarray, rf: float = 0.0) -> float:
        """Portfolio Sharpe ratio."""
        ret = np.dot(weights, expected_returns) - rf
        vol = np.sqrt(max(weights @ cov @ weights, 1e-8))
        return float(ret / vol)

    @staticmethod
    def calculate_composite_objective(
        weights: np.ndarray,
        expected_returns: np.ndarray,
        cov: np.ndarray,
        risk_aversion: float = 2.0
    ) -> float:
        """Mean-Variance utility: w^T mu - (gamma / 2) * w^T Sigma w."""
        ret = np.dot(weights, expected_returns)
        var = weights @ cov @ weights
        return float(ret - (risk_aversion / 2.0) * var)
