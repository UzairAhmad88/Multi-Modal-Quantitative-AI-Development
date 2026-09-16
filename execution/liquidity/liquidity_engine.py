"""
Liquidity Engine for assessing market volume capacity, participation limits, and partial fill capacity.
"""

from typing import Dict, Any, Tuple


class LiquidityEngine:
    """Evaluates market liquidity and caps order fill quantities based on max participation rate."""

    def __init__(self, max_participation_rate: float = 0.10, default_adv: float = 1000000.0):
        self.max_participation_rate = max_participation_rate
        self.default_adv = default_adv

    def evaluate_fill_capacity(
        self,
        requested_quantity: float,
        market_volume: float = 100000.0,
        adv: float = 1000000.0
    ) -> Dict[str, Any]:
        """Calculates maximum fill quantity allowed under configured participation caps."""
        eff_vol = market_volume if market_volume > 0 else (adv / 10.0 if adv > 0 else self.default_adv / 10.0)
        max_fillable = eff_vol * self.max_participation_rate

        filled_qty = min(requested_quantity, max_fillable)
        remaining_qty = max(0.0, requested_quantity - filled_qty)
        is_partial = remaining_qty > 1e-6
        participation_rate = (filled_qty / eff_vol) if eff_vol > 0 else 0.0

        return {
            "requested_quantity": requested_quantity,
            "filled_quantity": round(filled_qty, 4),
            "remaining_quantity": round(remaining_qty, 4),
            "is_partial_fill": is_partial,
            "market_volume": eff_vol,
            "max_fillable": round(max_fillable, 4),
            "participation_rate": round(participation_rate, 4),
            "max_participation_rate": self.max_participation_rate
        }
