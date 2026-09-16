"""
POV (Percentage of Volume) Execution Algorithm.
Executes child order slices targeting a maximum participation rate relative to market volume.
"""

from typing import List, Dict, Any
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide, TimeInForce


class POVExecutionAlgorithm:
    """POV Execution Strategy."""

    def __init__(self, target_participation_rate: float = 0.05, interval_volume: float = 20000.0):
        self.name = "POV"
        self.target_participation_rate = target_participation_rate
        self.interval_volume = interval_volume

    def generate_slices(self, order: Order, **kwargs) -> List[Order]:
        """Generates dynamic slice sizes bounded by volume participation rate."""
        total_qty = order.remaining_quantity
        if total_qty <= 0:
            return []

        market_vol = kwargs.get("market_volume", self.interval_volume)
        max_slice_qty = market_vol * self.target_participation_rate

        slices = []
        rem = total_qty
        while rem > 1e-6:
            q = min(rem, max_slice_qty)
            slices.append(Order(
                asset=order.asset,
                side=order.side,
                quantity=round(max(0.001, q), 4),
                order_type=OrderType.MARKET,
                time_in_force=order.time_in_force
            ))
            rem -= q

        return slices
