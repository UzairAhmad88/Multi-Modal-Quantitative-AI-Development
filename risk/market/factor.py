"""
Factor Risk Exposure Integration for Advanced Risk Engine OS.
"""

from typing import Dict, Any, Optional
import numpy as np


class FactorRiskEngine:
    """Computes portfolio and asset exposures to standard equity risk factors."""

    SUPPORTED_FACTORS = ["market", "size", "value", "momentum", "volatility", "quality"]

    @staticmethod
    def compute_factor_exposures(
        portfolio_returns: np.ndarray,
        factor_returns: Dict[str, np.ndarray],
    ) -> Dict[str, float]:
        """Regress portfolio returns against configured factor return series."""
        exposures = {}
        y = np.array(portfolio_returns, dtype=float)

        for factor_name, f_rets in factor_returns.items():
            if factor_name.lower() in FactorRiskEngine.SUPPORTED_FACTORS:
                x = np.array(f_rets, dtype=float)
                if len(x) == len(y) and len(x) > 2:
                    var_x = float(np.var(x, ddof=1))
                    if var_x > 1e-12:
                        cov_xy = float(np.cov(x, y)[0, 1])
                        exposures[factor_name] = float(cov_xy / var_x)
                    else:
                        exposures[factor_name] = 0.0

        return exposures
