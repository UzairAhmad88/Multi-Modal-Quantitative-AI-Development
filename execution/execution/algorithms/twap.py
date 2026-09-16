"""
TWAP (Time-Weighted Average Price) Execution Algorithm.
Divides parent order quantity evenly across N time intervals.
"""

from typing import List, Dict, Any
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide, TimeInForce


class TWAPExecutionAlgorithm:
    """TWAP Execution Strategy."""

    def __init__(self, num_intervals: int = 5):
        self.name = "TWAP"
        self.num_intervals = max(1, num_intervals)

    def generate_slices(self, order: Order, **kwargs) -> List[Order]:
        """Divides parent order into N equal slice orders across time steps."""
        total_qty = order.remaining_quantity
        if total_qty <= 0:
            return []

        slice_qty = total_qty / self.num_intervals
        slices = []
        for i in range(self.num_intervals):
            # Last slice handles potential float rounding delta
            q = slice_qty if i < self.num_intervals - 1 else (total_qty - (slice_qty * (self.num_intervals - 1)))
            slices.append(Order(
                asset=order.asset,
                side=order.side,
                quantity=round(max(0.001, q), 4),
                order_type=OrderType.MARKET,
                time_in_force=order.time_in_force
            ))
        return slices
