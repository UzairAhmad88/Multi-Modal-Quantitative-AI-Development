"""
Standardized Order Dataclass for Execution Engine.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from execution.orders.order_types import OrderType, OrderSide, TimeInForce
from execution.orders.order_status import OrderStatus


@dataclass
class Order:
    asset: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.DAY
    order_id: str = field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    rejection_reason: Optional[str] = None

    @property
    def remaining_quantity(self) -> float:
        return max(0.0, self.quantity - self.filled_quantity)

    @property
    def is_complete(self) -> bool:
        return self.status in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["side"] = self.side.value if isinstance(self.side, Enum) else str(self.side)
        data["order_type"] = self.order_type.value if isinstance(self.order_type, Enum) else str(self.order_type)
        data["time_in_force"] = self.time_in_force.value if isinstance(self.time_in_force, Enum) else str(self.time_in_force)
        data["status"] = self.status.value if isinstance(self.status, Enum) else str(self.status)
        data["remaining_quantity"] = self.remaining_quantity
        return data


from enum import Enum
