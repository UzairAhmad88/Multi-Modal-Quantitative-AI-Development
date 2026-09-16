"""
VWAP (Volume-Weighted Average Price) Execution Algorithm.
Allocates parent order quantity across intervals proportional to an intraday volume profile.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide, TimeInForce


class VWAPExecutionAlgorithm:
    """VWAP Execution Strategy."""

    def __init__(self, volume_profile: Optional[List[float]] = None):
        self.name = "VWAP"
        # Standard U-shaped intraday volume profile default (higher open/close, lower midday)
        self.volume_profile = volume_profile or [0.25, 0.15, 0.10, 0.15, 0.35]

    def generate_slices(self, order: Order, **kwargs) -> List[Order]:
        """Divides parent order into slices weighted by expected market volume profile."""
        total_qty = order.remaining_quantity
        if total_qty <= 0:
            return []

        weights = np.array(self.volume_profile, dtype=float)
        weights = weights / weights.sum()

        slices = []
        allocated = 0.0
        n = len(weights)
        for i, w in enumerate(weights):
            if i == n - 1:
                q = total_qty - allocated
            else:
                q = total_qty * w
                allocated += q

            slices.append(Order(
                asset=order.asset,
                side=order.side,
                quantity=round(max(0.001, q), 4),
                order_type=OrderType.MARKET,
                time_in_force=order.time_in_force
            ))
        return slices
