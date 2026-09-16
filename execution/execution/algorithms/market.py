"""
Market Execution Algorithm: Executes parent order immediately as a market order slice.
"""

from typing import List, Dict, Any
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide, TimeInForce


class MarketExecutionAlgorithm:
    """Standard Market Order Execution."""

    def __init__(self):
        self.name = "MARKET"

    def generate_slices(self, order: Order, **kwargs) -> List[Order]:
        """Returns single market order slice."""
        slice_order = Order(
            asset=order.asset,
            side=order.side,
            quantity=order.remaining_quantity,
            order_type=OrderType.MARKET,
            time_in_force=order.time_in_force
        )
        return [slice_order]
