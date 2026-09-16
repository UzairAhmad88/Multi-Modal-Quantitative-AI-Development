"""
Portfolio Optimization Allocators and Mathematical Solvers.
Includes Equal Weight, Inverse Volatility, Signal Weighting, Risk Parity, Mean-Variance, Minimum Variance, and Target Volatility algorithms.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from scipy.optimize import minimize

from portfolio_optimization.estimators.covariance import CovarianceEstimator
from portfolio_optimization.constraints.constraint_engine import ConstraintEngine


class EqualWeightAllocator:
    """Allocates 1/N equal weights across active asset universe."""

    @staticmethod
    def allocate(assets: List[str]) -> Dict[str, float]:
        if not assets:
            return {}
        w = 1.0 / len(assets)
        return {a: round(w, 6) for a in assets}


class InverseVolatilityAllocator:
    """Allocates weights inversely proportional to asset volatility."""

    @staticmethod
    def allocate(cov: np.ndarray, assets: List[str]) -> Dict[str, float]:
        if not assets or cov.size == 0:
            return {}
        vols = np.sqrt(np.diag(cov))
        vols = np.where(vols > 1e-6, vols, 1e-6)
        inv_vols = 1.0 / vols
        weights = inv_vols / np.sum(inv_vols)
        return {assets[i]: float(round(weights[i], 6)) for i in range(len(assets))}


class SignalWeightAllocator:
    """Allocates weights proportional to normalized positive alpha signals."""

    @staticmethod
    def allocate(signals: Dict[str, float]) -> Dict[str, float]:
        if not signals:
            return {}
        assets = list(signals.keys())
        raw_vals = np.array([signals[a] for a in assets], dtype=float)
        clipped = np.clip(raw_vals, 0.0, None)
        total = np.sum(clipped)
        if total > 1e-6:
            weights = clipped / total
        else:
            weights = np.ones(len(assets)) / len(assets)
        return {assets[i]: float(round(weights[i], 6)) for i in range(len(assets))}


class RiskParityAllocator:
    """Allocates portfolio to achieve equal risk contribution across all assets."""

    @staticmethod
    def allocate(cov: np.ndarray, assets: List[str]) -> Dict[str, float]:
        if not assets or cov.size == 0:
            return {}
        n = len(assets)

        def risk_budget_objective(w):
            w = np.array(w)
            port_vol = np.sqrt(max(w @ cov @ w, 1e-8))
            mcr = (cov @ w) / port_vol
            risk_contribs = w * mcr
            target_risk = port_vol / n
            return np.sum((risk_contribs - target_risk) ** 2)

        init_w = np.ones(n) / n
        bounds = [(0.0, 1.0) for _ in range(n)]
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})

        res = minimize(risk_budget_objective, init_w, method='SLSQP', bounds=bounds, constraints=constraints)
        weights = res.x if res.success else init_w
        weights = weights / np.sum(weights)
        return {assets[i]: float(round(weights[i], 6)) for i in range(n)}


class MeanVarianceOptimizer:
    """Mean-Variance Optimizer (Markowitz) maximizing expected return minus risk aversion x variance."""

    @staticmethod
    def allocate(
        expected_returns: Dict[str, float],
        cov: np.ndarray,
        assets: List[str],
        risk_aversion: float = 2.0,
        constraint_engine: Optional[ConstraintEngine] = None
    ) -> Dict[str, float]:
        if not assets or cov.size == 0:
            return {}
        n = len(assets)
        mu = np.array([expected_returns.get(a, 0.0) for a in assets])

        def utility_objective(w):
            ret = np.dot(w, mu)
            var = w @ cov @ w
            return -(ret - (risk_aversion / 2.0) * var)

        init_w = np.ones(n) / n
        b_max = constraint_engine.max_weight if constraint_engine else 0.35
        b_min = 0.0 if (not constraint_engine or constraint_engine.long_only) else constraint_engine.min_weight
        bounds = [(b_min, b_max) for _ in range(n)]
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})

        res = minimize(utility_objective, init_w, method='SLSQP', bounds=bounds, constraints=constraints)
        weights = res.x if res.success else init_w
        weights = np.clip(weights, 0.0, None)
        if np.sum(weights) > 1e-6:
            weights /= np.sum(weights)

        res_dict = {assets[i]: float(round(weights[i], 6)) for i in range(n)}
        if constraint_engine:
            res_dict = constraint_engine.apply_projection(res_dict)
        return res_dict


class MinimumVarianceOptimizer:
    """Global Minimum Variance Portfolio Optimizer."""

    @staticmethod
    def allocate(cov: np.ndarray, assets: List[str]) -> Dict[str, float]:
        if not assets or cov.size == 0:
            return {}
        n = len(assets)

        def var_objective(w):
            return w @ cov @ w

        init_w = np.ones(n) / n
        bounds = [(0.0, 1.0) for _ in range(n)]
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})

        res = minimize(var_objective, init_w, method='SLSQP', bounds=bounds, constraints=constraints)
        weights = res.x if res.success else init_w
        weights = weights / np.sum(weights)
        return {assets[i]: float(round(weights[i], 6)) for i in range(n)}


class TargetVolatilityOptimizer:
    """Scales portfolio weights to achieve explicit target annualized volatility."""

    @staticmethod
    def allocate(base_weights: Dict[str, float], cov: np.ndarray, assets: List[str], target_vol: float = 0.15) -> Dict[str, float]:
        if not base_weights or cov.size == 0:
            return {}
        w = np.array([base_weights.get(a, 0.0) for a in assets])
        current_vol = np.sqrt(max(w @ cov @ w, 1e-8))

        scale = target_vol / current_vol if current_vol > 1e-6 else 1.0
        w_scaled = w * scale
        w_scaled = np.clip(w_scaled, 0.0, 1.0)
        total = np.sum(w_scaled)
        if total > 1.0:
            w_scaled /= total

        return {assets[i]: float(round(w_scaled[i], 6)) for i in range(len(assets))}
