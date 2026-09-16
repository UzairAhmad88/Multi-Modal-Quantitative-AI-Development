"""
Position Object for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Position:
    symbol: str
    quantity: float
    price: float
    market_value: float
    weight: float
    side: str = "LONG"
    sector: str = "Unassigned"
    asset_class: str = "EQUITY"
    volatility: float = 0.0
    liquidity: float = 0.0

    def update_market_value(self, current_price: float, total_portfolio_value: float) -> None:
        """Update market value and weight based on new asset price."""
        self.price = current_price
        self.market_value = self.quantity * self.price
        if total_portfolio_value > 0:
            self.weight = self.market_value / total_portfolio_value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        return cls(
            symbol=data["symbol"],
            quantity=data.get("quantity", 0.0),
            price=data.get("price", 0.0),
            market_value=data.get("market_value", 0.0),
            weight=data.get("weight", 0.0),
            side=data.get("side", "LONG"),
            sector=data.get("sector", "Unassigned"),
            asset_class=data.get("asset_class", "EQUITY"),
            volatility=data.get("volatility", 0.0),
            liquidity=data.get("liquidity", 0.0),
        )
