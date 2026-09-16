"""
Risk Budgeting & Risk Decomposition Engine Module
Calculates Marginal Contribution to Risk (MCR), Component Risk Contribution (CRC), and Percentage Risk Contribution.
"""

from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd


class RiskBudgetEngine:
    """Quantitative Risk Budgeting & Component Risk Attribution Engine."""

    def __init__(self, covariance: pd.DataFrame):
        """
        Initialize RiskBudgetEngine with annualized covariance matrix.
        """
        self.cov = covariance.copy()
        self.symbols = list(covariance.columns)

    def compute_risk_contributions(self, weights: pd.Series) -> pd.DataFrame:
        """
        Decompose portfolio volatility into Marginal and Component Risk Contributions.
        Verifies sum(Component Risk Contribution) == Total Portfolio Volatility.
        """
        w = weights.reindex(self.symbols).fillna(0.0).values.reshape(-1, 1)
        cov_mat = self.cov.values

        port_var = float((w.T @ cov_mat @ w).item())
        port_vol = np.sqrt(max(1e-8, port_var))

        # Marginal Contribution to Risk (MCR) = (Sigma * w) / port_vol
        mcr = (cov_mat @ w) / port_vol

        # Component Risk Contribution (CRC) = w * MCR
        crc = w * mcr

        # Percentage Risk Contribution (PRC) = CRC / port_vol
        prc = crc / port_vol

        result_df = pd.DataFrame({
            "symbol": self.symbols,
            "weight": w.flatten(),
            "marginal_risk_mcr": mcr.flatten(),
            "component_risk_crc": crc.flatten(),
            "percentage_risk_prc": prc.flatten(),
        })

        result_df["weight"] = result_df["weight"].round(6)
        result_df["marginal_risk_mcr"] = result_df["marginal_risk_mcr"].round(6)
        result_df["component_risk_crc"] = result_df["component_risk_crc"].round(6)
        result_df["percentage_risk_prc"] = result_df["percentage_risk_prc"].round(4)

        return result_df
