"""
Value at Risk (VaR) Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, Optional
import numpy as np
from scipy.stats import norm


class VaREngine:
    """Computes Historical, Parametric, and Monte Carlo Value at Risk (VaR)."""

    @staticmethod
    def historical_var(
        portfolio_returns: np.ndarray,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
    ) -> float:
        """Historical VaR using empirical return quantiles."""
        r = np.array(portfolio_returns, dtype=float)
        if len(r) == 0:
            return 0.0

        alpha = 1.0 - confidence_level
        var_1d = float(-np.percentile(r, alpha * 100.0))
        var_h = var_1d * np.sqrt(horizon_days)
        return float(max(0.0, var_h))

    @staticmethod
    def parametric_var(
        portfolio_returns: np.ndarray,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
    ) -> float:
        """Parametric VaR assuming normal distribution: mu - z * sigma."""
        r = np.array(portfolio_returns, dtype=float)
        if len(r) < 2:
            return 0.0

        mu = float(np.mean(r))
        sigma = float(np.std(r, ddof=1))
        z = float(norm.ppf(confidence_level))

        var_1d = z * sigma - mu
        var_h = var_1d * np.sqrt(horizon_days)
        return float(max(0.0, var_h))

    @staticmethod
    def monte_carlo_var(
        simulated_pnl: np.ndarray,
        confidence_level: float = 0.95,
    ) -> float:
        """Monte Carlo VaR from simulated P&L distribution."""
        pnl = np.array(simulated_pnl, dtype=float)
        if len(pnl) == 0:
            return 0.0

        alpha = 1.0 - confidence_level
        var_val = float(-np.percentile(pnl, alpha * 100.0))
        return float(max(0.0, var_val))
