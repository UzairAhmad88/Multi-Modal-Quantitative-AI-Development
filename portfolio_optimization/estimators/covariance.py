"""
Covariance Matrix Estimator and Positive Semi-Definite Matrix Stabilizer.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.covariance import LedoitWolf


class CovarianceEstimator:
    """Estimates and validates sample, EWMA, and Ledoit-Wolf shrinkage covariance matrices."""

    @staticmethod
    def estimate_covariance(
        returns_df: pd.DataFrame,
        method: str = "shrinkage",
        annualize: bool = True
    ) -> Tuple[np.ndarray, List[str]]:
        """Estimates covariance matrix for asset universe."""
        if returns_df.empty:
            return np.array([[]]), []

        clean_df = returns_df.dropna(how="any")
        if clean_df.empty or len(clean_df) < 5:
            clean_df = returns_df.fillna(0.0)

        assets = list(clean_df.columns)
        n_assets = len(assets)

        if n_assets == 0:
            return np.array([[]]), []

        vals = clean_df.values

        if method == "shrinkage" and len(clean_df) >= n_assets:
            lw = LedoitWolf()
            cov = lw.fit(vals).covariance_
        elif method == "ewma":
            weights = np.exp(-np.arange(len(vals))[::-1] / 60.0)
            weights /= weights.sum()
            mean = np.average(vals, axis=0, weights=weights)
            diff = vals - mean
            cov = (diff.T * weights) @ diff
        else:  # sample
            cov = np.cov(vals, rowvar=False)
            if cov.ndim == 0:
                cov = np.array([[float(cov)]])

        if annualize:
            cov = cov * 252.0

        cov_stabilized = CovarianceEstimator.stabilize_psd(cov)
        return cov_stabilized, assets

    @staticmethod
    def stabilize_psd(cov: np.ndarray, min_eig: float = 1e-6) -> np.ndarray:
        """Validates and enforces Positive Semi-Definiteness via eigenvalue clipping."""
        if cov.size == 0:
            return cov

        # Ensure symmetry
        cov_sym = (cov + cov.T) / 2.0
        eigs, vecs = np.linalg.eigh(cov_sym)
        if np.any(eigs < min_eig):
            eigs = np.clip(eigs, min_eig, None)
            cov_sym = vecs @ np.diag(eigs) @ vecs.T

        return cov_sym
