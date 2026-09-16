"""
Market Impact Engine modeling square-root price impact as a function of trade size, ADV, and volatility.
"""

import numpy as np
from typing import Dict, Any


class MarketImpactEngine:
    """Calculates non-linear market impact penalty: Impact_bps = eta * volatility * sqrt(Trade_Size / ADV) * 10000."""

    def __init__(self, impact_coefficient: float = 0.5):
        self.impact_coefficient = impact_coefficient

    def calculate_impact(
        self,
        order_quantity: float,
        price: float,
        adv: float = 1000000.0,
        volatility: float = 0.02
    ) -> Dict[str, Any]:
        """Estimates market impact cost and impact in basis points."""
        trade_value = order_quantity * price
        adv_value = adv * price if price > 0 else adv

        ratio = (order_quantity / adv) if adv > 0 else 0.001
        ratio = max(1e-6, ratio)

        impact_bps = self.impact_coefficient * (volatility * 10000.0) * np.sqrt(ratio)
        impact_cost = trade_value * (impact_bps / 10000.0)

        return {
            "order_quantity": order_quantity,
            "trade_value": round(trade_value, 2),
            "adv": adv,
            "ratio_of_adv": round(ratio, 6),
            "impact_bps": round(impact_bps, 2),
            "impact_cost": round(impact_cost, 2)
        }
