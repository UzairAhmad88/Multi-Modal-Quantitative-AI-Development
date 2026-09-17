"""
Order Management System (OMS) for tracking order state transitions and lifecycle.
"""

from typing import Dict, List, Optional, Any
from execution.orders.order import Order
from execution.orders.order_status import OrderStatus
from execution.order_management.validation import OrderValidator


class OrderManager:
    """Manages order queue, status updates, and lifecycle audit trail."""

    def __init__(self, validator: Optional[OrderValidator] = None):
        self.validator = validator or OrderValidator()
        self.orders: Dict[str, Order] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.idempotency_map: Dict[str, str] = {}  # idempotency_key / signal_id -> order_id

    def create_order(self, order: Order, price: Optional[float] = None, idempotency_key: Optional[str] = None, signal_id: Optional[str] = None) -> Order:
        """Validates and registers a new order into the OMS with idempotency protection."""
        key = idempotency_key or signal_id
        if key and key in self.idempotency_map:
            existing_id = self.idempotency_map[key]
            order.status = OrderStatus.REJECTED
            order.rejection_reason = f"DUPLICATE_ORDER_BLOCKED: Signal/Key '{key}' already processed in Order '{existing_id}'"
            self.orders[order.order_id] = order
            self._record_event(order, "DUPLICATE_REJECTED")
            return order

        valid, reason = self.validator.validate(order, price=price)
        if not valid:
            order.status = OrderStatus.REJECTED
            order.rejection_reason = reason
        else:
            order.status = OrderStatus.SUBMITTED
            if key:
                self.idempotency_map[key] = order.order_id

        self.orders[order.order_id] = order
        self._record_event(order, f"ORDER_{order.status.value}")
        return order

    def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        filled_qty: float = 0.0,
        fill_price: float = 0.0,
        reason: Optional[str] = None
    ) -> Optional[Order]:
        """Updates status, fill progress, and audit trail of an order."""
        if order_id not in self.orders:
            return None

        order = self.orders[order_id]
        order.status = status
        if filled_qty > 0:
            total_qty = order.filled_quantity + filled_qty
            if total_qty > 0:
                order.avg_fill_price = ((order.filled_quantity * order.avg_fill_price) + (filled_qty * fill_price)) / total_qty
            order.filled_quantity = min(order.quantity, total_qty)

        if reason:
            order.rejection_reason = reason

        self._record_event(order, f"STATUS_{status.value}")
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def get_all_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        if status is None:
            return list(self.orders.values())
        return [o for o in self.orders.values() if o.status == status]

    def cancel_order(self, order_id: str, reason: str = "User Cancelled") -> bool:
        order = self.orders.get(order_id)
        if not order or order.is_complete:
            return False
        order.status = OrderStatus.CANCELLED
        order.rejection_reason = reason
        self._record_event(order, "ORDER_CANCELLED")
        return True

    def _record_event(self, order: Order, event_type: str):
        self.audit_log.append({
            "timestamp": order.timestamp,
            "order_id": order.order_id,
            "asset": order.asset,
            "event": event_type,
            "status": order.status.value,
            "filled_quantity": order.filled_quantity,
            "avg_fill_price": order.avg_fill_price
        })
