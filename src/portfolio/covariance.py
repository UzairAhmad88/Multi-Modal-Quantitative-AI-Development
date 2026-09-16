"""
Covariance Estimation & Stability Diagnostics Module
Calculates Sample Covariance, EWMA Covariance, and Ledoit-Wolf Shrinkage Covariance matrices with condition number diagnostics.
"""

from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd


class CovarianceEstimator:
    """Quantitative Covariance Estimation & Numerical Stability Engine."""

    def __init__(self, returns_df: pd.DataFrame):
        """
        Initialize CovarianceEstimator.
        :param returns_df: DataFrame of asset asset return series (columns=symbols).
        """
        self.df = returns_df.dropna().copy()

    def compute_sample_covariance(self, annualize: bool = True) -> pd.DataFrame:
        """Sample Covariance matrix."""
        cov = self.df.cov()
        if annualize:
            cov = cov * 252.0
        return self._ensure_psd(cov)

    def compute_ewma_covariance(self, decay_factor: float = 0.94, annualize: bool = True) -> pd.DataFrame:
        """Exponentially Weighted Moving Average (EWMA) Covariance."""
        rets = self.df.values
        n_samples, n_assets = rets.shape

        weights = (1 - decay_factor) * (decay_factor ** np.arange(n_samples)[::-1])
        weights = weights / np.sum(weights)

        mean_rets = np.average(rets, axis=0, weights=weights)
        demeaned = rets - mean_rets

        ewma_cov = np.zeros((n_assets, n_assets))
        for t in range(n_samples):
            row = demeaned[t, :].reshape(-1, 1)
            ewma_cov += weights[t] * (row @ row.T)

        if annualize:
            ewma_cov = ewma_cov * 252.0

        cov_df = pd.DataFrame(ewma_cov, index=self.df.columns, columns=self.df.columns)
        return self._ensure_psd(cov_df)

    def compute_shrinkage_covariance(self, shrinkage_target: str = "constant_variance", annualize: bool = True) -> pd.DataFrame:
        """Ledoit-Wolf Shrinkage Covariance Estimator."""
        sample_cov = self.df.cov().values
        n_assets = sample_cov.shape[0]

        # Target: Constant variance matrix
        mean_var = np.trace(sample_cov) / n_assets
        target = mean_var * np.eye(n_assets)

        # Simple shrinkage intensity alpha = 0.20
        alpha = 0.20
        shrunk_cov = (1 - alpha) * sample_cov + alpha * target

        if annualize:
            shrunk_cov = shrunk_cov * 252.0

        cov_df = pd.DataFrame(shrunk_cov, index=self.df.columns, columns=self.df.columns)
        return self._ensure_psd(cov_df)

    def check_stability(self, cov_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate matrix condition number, eigenvalues, and positive semi-definiteness.
        """
        matrix = cov_df.values
        eigenvalues = np.linalg.eigvalsh(matrix)
        min_eig = float(np.min(eigenvalues))
        max_eig = float(np.max(eigenvalues))
        cond_num = float(max_eig / (min_eig + 1e-12)) if min_eig > 0 else float("inf")

        return {
            "is_positive_definite": bool(min_eig > 1e-8),
            "min_eigenvalue": round(min_eig, 6),
            "max_eigenvalue": round(max_eig, 6),
            "condition_number": round(cond_num, 4) if cond_num != float("inf") else 999999.0,
            "is_well_conditioned": bool(cond_num < 1000.0),
        }

    @staticmethod
    def _ensure_psd(cov_df: pd.DataFrame) -> pd.DataFrame:
        """Project matrix onto nearest positive semi-definite matrix if needed."""
        matrix = cov_df.values
        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        if np.min(eigenvalues) < 1e-8:
            eigenvalues = np.maximum(eigenvalues, 1e-6)
            psd_matrix = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
            return pd.DataFrame(psd_matrix, index=cov_df.index, columns=cov_df.columns)
        return cov_df
