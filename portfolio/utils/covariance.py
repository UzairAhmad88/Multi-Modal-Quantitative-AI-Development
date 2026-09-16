"""
Covariance Estimation and Validation Utilities for Portfolio Construction OS.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


class CovarianceEstimator:
    """Covariance estimation, shrinkage, and matrix condition diagnostics."""

    @staticmethod
    def sample_covariance(returns: np.ndarray, annualize: bool = True, scale_factor: int = 252) -> np.ndarray:
        """Compute sample covariance matrix."""
        cov = np.cov(returns, rowvar=False)
        if cov.ndim == 0:
            cov = np.array([[float(cov)]])
        if annualize:
            cov = cov * scale_factor
        return cov

    @staticmethod
    def ewma_covariance(returns: np.ndarray, halflife: int = 60, annualize: bool = True, scale_factor: int = 252) -> np.ndarray:
        """Compute exponentially weighted moving average covariance matrix."""
        df = pd.DataFrame(returns)
        ewma_cov = df.ewm(halflife=halflife).cov().values[-returns.shape[1]:]
        if annualize:
            ewma_cov = ewma_cov * scale_factor
        return ewma_cov

    @staticmethod
    def validate_covariance(cov: np.ndarray) -> Tuple[bool, Dict[str, Any]]:
        """Validate matrix symmetry, positive semi-definiteness, and condition number."""
        n = cov.shape[0]
        diagnostics = {
            "is_square": cov.ndim == 2 and cov.shape[0] == cov.shape[1],
            "has_nan": bool(np.isnan(cov).any()),
            "is_symmetric": bool(np.allclose(cov, cov.T, atol=1e-6)),
        }

        if not diagnostics["is_square"] or diagnostics["has_nan"]:
            diagnostics["is_positive_semidefinite"] = False
            diagnostics["condition_number"] = float("inf")
            return False, diagnostics

        eigenvalues = np.linalg.eigvalsh(cov)
        min_eig = float(np.min(eigenvalues))
        max_eig = float(np.max(eigenvalues))

        diagnostics["min_eigenvalue"] = min_eig
        diagnostics["max_eigenvalue"] = max_eig
        diagnostics["is_positive_semidefinite"] = min_eig >= -1e-8

        if min_eig > 0:
            diagnostics["condition_number"] = float(max_eig / min_eig)
        else:
            diagnostics["condition_number"] = float("inf")

        is_valid = diagnostics["is_symmetric"] and diagnostics["is_positive_semidefinite"]
        return is_valid, diagnostics

    @staticmethod
    def ledoit_wolf_shrinkage(cov: np.ndarray, shrinkage_target: str = "equal_variance") -> np.ndarray:
        """Apply Ledoit-Wolf shrinkage to regularize ill-conditioned covariance matrix."""
        n = cov.shape[0]
        if shrinkage_target == "equal_variance":
            target = np.eye(n) * np.trace(cov) / n
        else:
            target = np.diag(np.diag(cov))

        delta = 0.2  # Regularization parameter
        shrunken_cov = (1.0 - delta) * cov + delta * target
        return shrunken_cov
