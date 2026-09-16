"""
Portfolio Risk Contribution & Reconciliation Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class RiskContributionEngine:
    """Computes Marginal (MCR), Component (CCR), and Percentage (PCR) Risk Contributions."""

    @staticmethod
    def compute_contributions(
        weights: Dict[str, float],
        cov_matrix: np.ndarray,
    ) -> Dict[str, Any]:
        assets = list(weights.keys())
        w = np.array([weights[a] for a in assets], dtype=float)
        cov = np.array(cov_matrix, dtype=float)

        port_var = float(w.T @ cov @ w)
        port_vol = np.sqrt(max(1e-12, port_var))

        mcr = (cov @ w) / port_vol
        ccr = w * mcr
        pcr = ccr / port_vol

        sum_ccr = float(np.sum(ccr))
        reconciled = bool(abs(sum_ccr - port_vol) < 1e-5)

        return {
            "portfolio_volatility": port_vol,
            "portfolio_variance": port_var,
            "marginal_contributions": {assets[i]: float(mcr[i]) for i in range(len(assets))},
            "component_contributions": {assets[i]: float(ccr[i]) for i in range(len(assets))},
            "percentage_contributions": {assets[i]: float(pcr[i]) for i in range(len(assets))},
            "sum_ccr": sum_ccr,
            "reconciled": reconciled,
        }
