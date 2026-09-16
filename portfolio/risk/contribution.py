"""
Risk Contribution Calculator for Portfolio Construction OS.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np


class RiskContributionCalculator:
    """Computes Marginal Contribution to Risk (MCR), Component Risk Contribution (CCR), and Percentage Risk Contribution (PCR)."""

    @staticmethod
    def calculate_risk_contributions(
        weights: np.ndarray,
        cov_matrix: np.ndarray,
        asset_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        w = np.array(weights, dtype=float)
        cov = np.array(cov_matrix, dtype=float)

        port_var = float(w.T @ cov @ w)
        port_vol = np.sqrt(max(1e-12, port_var))

        # Marginal Contribution to Risk (MCR): d(sigma_p)/dw = (Sigma * w) / sigma_p
        mcr = (cov @ w) / port_vol

        # Component Contribution to Risk (CCR): w_i * MCR_i
        ccr = w * mcr

        # Percentage Contribution to Risk (PCR): CCR_i / sigma_p
        pcr = ccr / port_vol

        names = asset_names or [f"Asset_{i}" for i in range(len(w))]

        res = {
            "portfolio_volatility": port_vol,
            "portfolio_variance": port_var,
            "mcr": {names[i]: float(mcr[i]) for i in range(len(w))},
            "ccr": {names[i]: float(ccr[i]) for i in range(len(w))},
            "pcr": {names[i]: float(pcr[i]) for i in range(len(w))},
        }
        return res
