"""
Slippage Engine for directional execution price adjustments based on fixed bps, percentage, volatility, and volume models.
"""

from typing import Dict, Any, Optional
from execution.orders.order_types import OrderSide


class SlippageEngine:
    """Calculates directional slippage penalty to ensure realistic execution prices."""

    def __init__(
        self,
        model: str = "fixed_bps",
        fixed_bps: float = 5.0,
        volatility_factor: float = 0.5,
        volume_factor: float = 0.1
    ):
        self.model = model
        self.fixed_bps = fixed_bps
        self.volatility_factor = volatility_factor
        self.volume_factor = volume_factor

    def calculate_execution_price(
        self,
        ref_price: float,
        side: OrderSide,
        quantity: float = 100.0,
        volume: float = 10000.0,
        volatility: float = 0.02
    ) -> Dict[str, float]:
        """Calculates adjusted execution price given directional slippage penalty."""
        if ref_price <= 0:
            return {"execution_price": ref_price, "slippage_bps": 0.0, "slippage_cost": 0.0}

        if self.model == "fixed_bps":
            slippage_bps = self.fixed_bps
        elif self.model == "volatility_based":
            slippage_bps = self.fixed_bps + (volatility * 10000.0 * self.volatility_factor)
        elif self.model == "volume_based":
            part_rate = (quantity / volume) if volume > 0 else 0.01
            slippage_bps = self.fixed_bps + (part_rate * 100.0 * self.volume_factor * 100.0)
        else:
            slippage_bps = self.fixed_bps

        price_delta = ref_price * (slippage_bps / 10000.0)

        # Directional adjustment: BUY/COVER pays HIGHER price, SELL/SHORT receives LOWER price
        if side in (OrderSide.BUY, OrderSide.COVER):
            exec_price = ref_price + price_delta
        elif side in (OrderSide.SELL, OrderSide.SHORT):
            exec_price = max(0.01, ref_price - price_delta)
        else:
            exec_price = ref_price

        slippage_cost = abs(exec_price - ref_price) * quantity

        return {
            "execution_price": round(exec_price, 4),
            "slippage_bps": round(slippage_bps, 2),
            "slippage_cost": round(slippage_cost, 2),
            "price_delta": round(price_delta, 4)
        }
