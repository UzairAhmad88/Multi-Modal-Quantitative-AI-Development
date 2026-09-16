"""
Limit Execution Algorithm: Executes parent order at or better than specified limit price.
"""

from typing import List, Dict, Any, Optional
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide, TimeInForce


class LimitExecutionAlgorithm:
    """Standard Limit Order Execution."""

    def __init__(self, limit_price: Optional[float] = None):
        self.name = "LIMIT"
        self.limit_price = limit_price

    def generate_slices(self, order: Order, **kwargs) -> List[Order]:
        """Returns single limit order slice."""
        p = self.limit_price if self.limit_price is not None else order.limit_price
        slice_order = Order(
            asset=order.asset,
            side=order.side,
            quantity=order.remaining_quantity,
            order_type=OrderType.LIMIT,
            limit_price=p,
            time_in_force=order.time_in_force
        )
        return [slice_order]
