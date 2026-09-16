"""
Order Validator for checking sanity, quantity, price, and portfolio constraint limits.
"""

from typing import Tuple, Optional, Dict, Any
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide
from execution.orders.order_status import OrderStatus


class OrderValidator:
    """Validates order structures prior to queue submission."""

    def __init__(self, max_order_value: float = 1000000.0, max_quantity: float = 100000.0):
        self.max_order_value = max_order_value
        self.max_quantity = max_quantity

    def validate(self, order: Order, price: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """Checks order field integrity and quantitative limits."""
        if not order.asset or not isinstance(order.asset, str):
            return False, "Invalid asset symbol"

        if order.quantity <= 0:
            return False, f"Non-positive order quantity: {order.quantity}"

        if order.quantity > self.max_quantity:
            return False, f"Order quantity {order.quantity} exceeds maximum allowed limit {self.max_quantity}"

        if order.order_type in (OrderType.LIMIT, OrderType.STOP_LIMIT):
            if order.limit_price is None or order.limit_price <= 0:
                return False, f"Invalid limit price for {order.order_type.value} order: {order.limit_price}"

        ref_price = order.limit_price if order.limit_price else price
        if ref_price and ref_price > 0:
            order_val = order.quantity * ref_price
            if order_val > self.max_order_value:
                return False, f"Order value ${order_val:,.2f} exceeds maximum threshold ${self.max_order_value:,.2f}"

        return True, None
