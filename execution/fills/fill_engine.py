"""
Fill Engine for generating execution fills, tracking remaining quantities, and recording transaction details.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from execution.orders.order import Order
from execution.orders.order_types import OrderSide


@dataclass
class Fill:
    fill_id: str
    order_id: str
    asset: str
    side: OrderSide
    quantity: float
    fill_price: float
    timestamp: str
    fees: float = 0.0
    slippage: float = 0.0
    execution_latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["side"] = self.side.value if hasattr(self.side, "value") else str(self.side)
        data["gross_value"] = round(self.quantity * self.fill_price, 2)
        return data


class FillEngine:
    """Manages fill creation and tracks filled order records."""

    def __init__(self):
        self.fills: List[Fill] = []

    def create_fill(
        self,
        order: Order,
        fill_qty: float,
        fill_price: float,
        timestamp: Optional[str] = None,
        fees: float = 0.0,
        slippage: float = 0.0,
        latency_ms: float = 0.0
    ) -> Fill:
        """Creates a fill record for an executed slice or order."""
        fill = Fill(
            fill_id=f"FILL-{uuid.uuid4().hex[:8].upper()}",
            order_id=order.order_id,
            asset=order.asset,
            side=order.side,
            quantity=fill_qty,
            fill_price=fill_price,
            timestamp=timestamp or datetime.utcnow().isoformat() + "Z",
            fees=fees,
            slippage=slippage,
            execution_latency_ms=latency_ms
        )
        self.fills.append(fill)
        return fill

    def get_fills_for_order(self, order_id: str) -> List[Fill]:
        return [f for f in self.fills if f.order_id == order_id]
