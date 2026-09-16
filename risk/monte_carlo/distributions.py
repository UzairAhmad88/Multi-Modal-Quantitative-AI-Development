"""
Return Distribution Generator for Monte Carlo Simulation OS.
"""

from typing import Dict, Any, Optional
import numpy as np


class ReturnDistribution:
    """Generates correlated asset return multivariate normal and empirical random paths."""

    @staticmethod
    def generate_correlated_normal(
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        num_simulations: int = 10000,
        horizon_days: int = 1,
        seed: int = 42,
    ) -> np.ndarray:
        """Generate correlated return scenarios: R ~ N(mu, Sigma) via Cholesky decomposition."""
        np.random.seed(seed)
        n_assets = len(mean_returns)

        # Scale mean and covariance for horizon
        mu = mean_returns * horizon_days
        cov = cov_matrix * horizon_days

        # Ensure positive semi-definite matrix for Cholesky
        min_eig = np.min(np.linalg.eigvalsh(cov))
        if min_eig < 1e-8:
            cov += np.eye(n_assets) * (1e-8 - min_eig)

        L = np.linalg.cholesky(cov)
        z = np.random.normal(size=(num_simulations, n_assets))
        simulated_returns = mu + (z @ L.T)
        return simulated_returns

    @staticmethod
    def generate_empirical_bootstrap(
        historical_returns: np.ndarray,
        num_simulations: int = 10000,
        seed: int = 42,
    ) -> np.ndarray:
        """Resample historical empirical return vectors to preserve cross-asset correlation."""
        np.random.seed(seed)
        n_obs = len(historical_returns)
        indices = np.random.choice(n_obs, size=num_simulations, replace=True)
        return historical_returns[indices]
