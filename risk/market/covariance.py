"""
Covariance Matrix Audit & Diagnostics for Advanced Risk Engine OS.
"""

from typing import Dict, Any, Tuple
import numpy as np


class CovarianceAudit:
    """Validates covariance matrix condition numbers, positive semi-definiteness, and symmetry."""

    @staticmethod
    def audit_covariance(cov_matrix: np.ndarray) -> Tuple[bool, Dict[str, Any]]:
        cov = np.array(cov_matrix, dtype=float)
        diagnostics = {
            "is_square": cov.ndim == 2 and cov.shape[0] == cov.shape[1],
            "has_nan": bool(np.isnan(cov).any()),
            "is_symmetric": bool(np.allclose(cov, cov.T, atol=1e-5)),
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
        diagnostics["is_positive_semidefinite"] = min_eig >= -1e-7

        if min_eig > 0:
            diagnostics["condition_number"] = float(max_eig / min_eig)
        else:
            diagnostics["condition_number"] = float("inf")

        is_valid = diagnostics["is_symmetric"] and diagnostics["is_positive_semidefinite"]
        return is_valid, diagnostics
