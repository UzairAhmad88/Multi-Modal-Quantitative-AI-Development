"""
Market Impact Model for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
import numpy as np


class MarketImpactModel:
    """Non-linear market impact model using square-root trade size scaling."""

    @staticmethod
    def calculate_impact_cost(
        trade_size_shares: float,
        adv_shares: float,
        daily_volatility: float,
        price: float,
        eta: float = 0.75,
    ) -> float:
        """Square-root market impact cost calculation in USD."""
        if adv_shares <= 0 or price <= 0:
            return 0.0

        participation = trade_size_shares / adv_shares
        impact_pct = eta * daily_volatility * np.sqrt(np.maximum(0.0, participation))
        impact_usd = trade_size_shares * price * impact_pct
        return float(impact_usd)
