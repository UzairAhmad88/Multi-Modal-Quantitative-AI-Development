"""
Liquidity Analytics: Tracks fill rate, partial fill rates, and rejection rates.
"""

from typing import List, Dict, Any
from execution.orders.order import Order
from execution.orders.order_status import OrderStatus


class LiquidityAnalytics:
    """Analyzes execution fill rate and order rejection metrics."""

    def analyze_liquidity(self, orders: List[Order]) -> Dict[str, Any]:
        """Calculates order fill rate, partial fill rate, and rejection percentage."""
        if not orders:
            return {"fill_rate": 0.0, "rejection_rate": 0.0, "total_orders": 0}

        total_orders = len(orders)
        filled = sum(1 for o in orders if o.status == OrderStatus.FILLED)
        partially_filled = sum(1 for o in orders if o.status == OrderStatus.PARTIALLY_FILLED)
        rejected = sum(1 for o in orders if o.status == OrderStatus.REJECTED)
        cancelled = sum(1 for o in orders if o.status == OrderStatus.CANCELLED)

        req_qty = sum(o.quantity for o in orders)
        filled_qty = sum(o.filled_quantity for o in orders)

        fill_rate = (filled_qty / req_qty) if req_qty > 0 else 0.0
        rejection_rate = (rejected / total_orders) if total_orders > 0 else 0.0

        return {
            "total_orders": total_orders,
            "filled_orders": filled,
            "partially_filled_orders": partially_filled,
            "rejected_orders": rejected,
            "cancelled_orders": cancelled,
            "requested_quantity": round(req_qty, 4),
            "filled_quantity": round(filled_qty, 4),
            "fill_rate": round(fill_rate, 4),
            "rejection_rate": round(rejection_rate, 4)
        }
