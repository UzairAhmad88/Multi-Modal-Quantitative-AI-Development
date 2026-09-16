"""
Portfolio Scenario Engine for Market, Volatility, Correlation, and Sector Shock Stress Testing.
"""

import numpy as np

from typing import Dict, Any, List


class ScenarioEngine:
    """Evaluates portfolio impact under synthetic macro and volatility market shocks."""

    @staticmethod
    def evaluate_market_shock(
        weights: Dict[str, float],
        shock_pct: float = -0.10
    ) -> Dict[str, Any]:
        """Evaluates portfolio impact from immediate market-wide price shock."""
        w_sum = sum(weights.values())
        portfolio_shock_impact = w_sum * shock_pct
        return {
            "scenario": f"Market Shock {shock_pct:.0%}",
            "gross_exposure": round(w_sum, 4),
            "estimated_impact": round(portfolio_shock_impact, 4)
        }

    @staticmethod
    def evaluate_volatility_spike(
        weights: Dict[str, float],
        cov: np.ndarray,
        vol_multiplier: float = 1.5
    ) -> Dict[str, Any]:
        """Evaluates portfolio volatility under a volatility spike scenario."""
        if cov.size == 0 or not weights:
            return {}
        w = np.array(list(weights.values()), dtype=float)
        base_vol = float(np.sqrt(max(w @ cov @ w, 1e-8)))
        shocked_cov = cov * (vol_multiplier ** 2)
        shocked_vol = float(np.sqrt(max(w @ shocked_cov @ w, 1e-8)))

        return {
            "scenario": f"Volatility Spike {vol_multiplier}x",
            "base_volatility": round(base_vol, 4),
            "shocked_volatility": round(shocked_vol, 4),
            "volatility_increase": round(shocked_vol - base_vol, 4)
        }
