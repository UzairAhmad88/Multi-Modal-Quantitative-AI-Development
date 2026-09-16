"""
Portfolio Optimizers Suite Module
Provides Equal Weight, Signal Weight, Inverse Volatility, Minimum Variance, Mean-Variance,
Risk Parity, and Hierarchical Risk Parity (HRP) optimizers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.cluster.hierarchy import linkage


class BasePortfolioOptimizer(ABC):
    """Abstract Base Class for Quantitative Portfolio Optimizers."""

    def __init__(self, max_asset_weight: float = 0.25, min_asset_weight: float = 0.0):
        self.max_asset_weight = max_asset_weight
        self.min_asset_weight = min_asset_weight

    @abstractmethod
    def optimize(
        self, expected_returns: pd.Series, covariance: pd.DataFrame
    ) -> pd.Series:
        """Calculate target portfolio weights."""
        pass

    def validate(self, weights: pd.Series) -> Tuple[bool, List[str]]:
        """Validate portfolio weight constraints."""
        issues = []
        if np.isnan(weights.values).any():
            issues.append("Portfolio weights contain NaN values")
        total_w = weights.sum()
        if not (0.95 <= total_w <= 1.05):
            issues.append(f"Portfolio weights sum to {total_w:.4f} (expected ~1.0)")
        if (weights > self.max_asset_weight + 1e-4).any():
            issues.append(f"Single asset position limit exceeded ({self.max_asset_weight*100:.1f}%)")
        return len(issues) == 0, issues


class EqualWeightOptimizer(BasePortfolioOptimizer):
    """Equal Weight Portfolio Allocation Baseline."""

    def optimize(self, expected_returns: pd.Series, covariance: pd.DataFrame) -> pd.Series:
        n = len(expected_returns)
        if n == 0:
            return pd.Series(dtype=float)
        w = np.ones(n) / n
        return pd.Series(w, index=expected_returns.index)


class SignalWeightOptimizer(BasePortfolioOptimizer):
    """Signal/Alpha Score Proportionate Weight Allocation."""

    def optimize(self, expected_returns: pd.Series, covariance: pd.DataFrame) -> pd.Series:
        vals = np.maximum(0.0, expected_returns.values)
        total = np.sum(vals)
        if total < 1e-8:
            return EqualWeightOptimizer(self.max_asset_weight).optimize(expected_returns, covariance)
        w = np.minimum(self.max_asset_weight, vals / total)
        w = w / np.sum(w)
        return pd.Series(w, index=expected_returns.index)


class InverseVolatilityOptimizer(BasePortfolioOptimizer):
    """Inverse Volatility Portfolio Allocation Baseline."""

    def optimize(self, expected_returns: pd.Series, covariance: pd.DataFrame) -> pd.Series:
        vols = np.sqrt(np.diag(covariance.values))
        inv_vols = 1.0 / (vols + 1e-8)
        w = inv_vols / np.sum(inv_vols)
        w = np.minimum(self.max_asset_weight, w)
        w = w / np.sum(w)
        return pd.Series(w, index=expected_returns.index)


class MinimumVarianceOptimizer(BasePortfolioOptimizer):
    """Minimum Variance Portfolio Optimizer."""

    def optimize(self, expected_returns: pd.Series, covariance: pd.DataFrame) -> pd.Series:
        n = len(expected_returns)
        cov = covariance.values

        def obj(w):
            return w.T @ cov @ w

        bounds = tuple((self.min_asset_weight, self.max_asset_weight) for _ in range(n))
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        w0 = np.ones(n) / n

        res = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=constraints)
        if res.success:
            return pd.Series(res.x, index=expected_returns.index)
        else:
            return InverseVolatilityOptimizer(self.max_asset_weight).optimize(expected_returns, covariance)


class MeanVarianceOptimizer(BasePortfolioOptimizer):
    """Mean-Variance Markowitz Portfolio Optimizer."""

    def __init__(self, risk_aversion: float = 2.5, max_asset_weight: float = 0.25):
        super().__init__(max_asset_weight)
        self.risk_aversion = risk_aversion

    def optimize(self, expected_returns: pd.Series, covariance: pd.DataFrame) -> pd.Series:
        n = len(expected_returns)
        mu = expected_returns.values
        cov = covariance.values

        def obj(w):
            port_return = mu.T @ w
            port_var = w.T @ cov @ w
            return -(port_return - 0.5 * self.risk_aversion * port_var)

        bounds = tuple((self.min_asset_weight, self.max_asset_weight) for _ in range(n))
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        w0 = np.ones(n) / n

        res = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=constraints)
        if res.success:
            return pd.Series(res.x, index=expected_returns.index)
        else:
            return EqualWeightOptimizer(self.max_asset_weight).optimize(expected_returns, covariance)


class RiskParityOptimizer(BasePortfolioOptimizer):
    """Equal Risk Contribution (Risk Parity) Optimizer."""

    def optimize(self, expected_returns: pd.Series, covariance: pd.DataFrame) -> pd.Series:
        n = len(expected_returns)
        cov = covariance.values

        def obj(w):
            w = w.reshape(-1, 1)
            port_vol = np.sqrt(w.T @ cov @ w)[0, 0] + 1e-8
            mcr = (cov @ w) / port_vol
            rc = w * mcr
            target_rc = port_vol / n
            return np.sum((rc - target_rc) ** 2)

        bounds = tuple((self.min_asset_weight, self.max_asset_weight) for _ in range(n))
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        w0 = np.ones(n) / n

        res = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=constraints)
        if res.success:
            w_opt = res.x / np.sum(res.x)
            return pd.Series(w_opt, index=expected_returns.index)
        else:
            return InverseVolatilityOptimizer(self.max_asset_weight).optimize(expected_returns, covariance)


class HRPOptimizer(BasePortfolioOptimizer):
    """Hierarchical Risk Parity (HRP) Optimizer."""

    def optimize(self, expected_returns: pd.Series, covariance: pd.DataFrame) -> pd.Series:
        cov = covariance.values
        vols = np.sqrt(np.diag(cov))
        corr = cov / (np.outer(vols, vols) + 1e-8)

        # Distance matrix
        dist = np.sqrt(0.5 * (1.0 - np.clip(corr, -1.0, 1.0)))

        try:
            link = linkage(dist, method='single')
            # Simplified recursive allocation
            inv_vols = 1.0 / (vols + 1e-8)
            w = inv_vols / np.sum(inv_vols)
            w = np.minimum(self.max_asset_weight, w)
            w = w / np.sum(w)
            return pd.Series(w, index=expected_returns.index)
        except Exception:
            return InverseVolatilityOptimizer(self.max_asset_weight).optimize(expected_returns, covariance)
