"""
Risk Contribution & Marginal Contribution to Risk (MCR) Engine.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple


class RiskAttributionEngine:
    """Calculates Marginal Contribution to Risk (MCR) and Percentage Risk Contribution (PCR)."""

    @staticmethod
    def calculate_risk_contributions(weights: Dict[str, float], cov: np.ndarray) -> Dict[str, Any]:
        """Calculates portfolio volatility, asset MCR, and percentage risk contribution."""
        if not weights or cov.size == 0:
            return {"portfolio_volatility": 0.0, "risk_contributions": {}}

        assets = list(weights.keys())
        w = np.array([weights[a] for a in assets], dtype=float)
        port_var = float(w @ cov @ w)
        port_vol = float(np.sqrt(max(port_var, 1e-8)))

        mcr = (cov @ w) / port_vol if port_vol > 1e-6 else np.zeros(len(assets))
        abs_risk_contrib = w * mcr
        pct_risk_contrib = (abs_risk_contrib / port_vol) if port_vol > 1e-6 else np.ones(len(assets)) / len(assets)

        contrib_dict = {}
        for i, a in enumerate(assets):
            contrib_dict[a] = {
                "weight": round(float(w[i]), 4),
                "mcr": round(float(mcr[i]), 4),
                "risk_contribution": round(float(abs_risk_contrib[i]), 4),
                "pct_risk_contribution": round(float(pct_risk_contrib[i]), 4)
            }

        return {
            "portfolio_volatility": round(port_vol, 4),
            "portfolio_variance": round(port_var, 6),
            "assets": contrib_dict
        }
