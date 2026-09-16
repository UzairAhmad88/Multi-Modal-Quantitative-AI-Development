"""
Implementation Shortfall Analytics: Measures total execution drag relative to decision price benchmark.
"""

from typing import Dict, Any, List
from execution.fills.fill_engine import Fill
from execution.orders.order import Order
from execution.orders.order_types import OrderSide


class ImplementationShortfall:
    """Calculates Per-Trade and Portfolio Implementation Shortfall."""

    def calculate_shortfall(
        self,
        fills: List[Fill],
        decision_prices: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculates implementation shortfall across all executed fills."""
        if not fills:
            return {"total_shortfall_dollars": 0.0, "total_shortfall_bps": 0.0, "by_asset": {}}

        total_shortfall = 0.0
        total_decision_val = 0.0
        by_asset = {}

        for fill in fills:
            p_dec = decision_prices.get(fill.asset, fill.fill_price)
            p_fill = fill.fill_price
            qty = fill.quantity
            side = fill.side

            dec_val = qty * p_dec
            total_decision_val += dec_val

            if side in (OrderSide.BUY, OrderSide.COVER):
                sf = (p_fill - p_dec) * qty + fill.fees
            else:
                sf = (p_dec - p_fill) * qty + fill.fees

            total_shortfall += sf

            if fill.asset not in by_asset:
                by_asset[fill.asset] = {"shortfall_dollars": 0.0, "decision_value": 0.0}
            by_asset[fill.asset]["shortfall_dollars"] += sf
            by_asset[fill.asset]["decision_value"] += dec_val

        shortfall_bps = (total_shortfall / total_decision_val * 10000.0) if total_decision_val > 0 else 0.0

        return {
            "total_shortfall_dollars": round(total_shortfall, 2),
            "total_shortfall_bps": round(shortfall_bps, 2),
            "total_decision_value": round(total_decision_val, 2),
            "by_asset": by_asset
        }
