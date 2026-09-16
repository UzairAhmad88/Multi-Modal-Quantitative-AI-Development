"""
Conditional Value at Risk (CVaR / Expected Shortfall) Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, Optional
import numpy as np


class CVaREngine:
    """Computes Conditional VaR (Expected Shortfall) across historical and simulated return distributions."""

    @staticmethod
    def calculate_cvar(
        portfolio_returns: np.ndarray,
        confidence_level: float = 0.95,
        horizon_days: int = 1,
    ) -> float:
        """Expected Shortfall: average loss beyond VaR threshold."""
        r = np.array(portfolio_returns, dtype=float)
        if len(r) == 0:
            return 0.0

        alpha = 1.0 - confidence_level
        cutoff = float(np.percentile(r, alpha * 100.0))

        tail_losses = r[r <= cutoff]
        if len(tail_losses) == 0:
            cvar_1d = float(-cutoff)
        else:
            cvar_1d = float(-np.mean(tail_losses))

        cvar_h = cvar_1d * np.sqrt(horizon_days)
        return float(max(0.0, cvar_h))
