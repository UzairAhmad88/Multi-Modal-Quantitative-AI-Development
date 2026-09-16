"""
Simulated Order Book representation (bids, asks, depths, spread calculation).
"""

from typing import List, Dict, Tuple, Any, Optional


class OrderBook:
    """Represents a snapshot of bids, asks, and liquidity depth for an asset."""

    def __init__(
        self,
        asset: str,
        bids: Optional[List[Tuple[float, float]]] = None,
        asks: Optional[List[Tuple[float, float]]] = None
    ):
        self.asset = asset
        self.bids = sorted(bids or [], key=lambda x: x[0], reverse=True)
        self.asks = sorted(asks or [], key=lambda x: x[0])

    @property
    def best_bid(self) -> Optional[float]:
        return self.bids[0][0] if self.bids else None

    @property
    def best_ask(self) -> Optional[float]:
        return self.asks[0][0] if self.asks else None

    @property
    def mid_price(self) -> Optional[float]:
        if self.best_bid is not None and self.best_ask is not None:
            return (self.best_bid + self.best_ask) / 2.0
        return self.best_bid or self.best_ask

    @property
    def spread(self) -> float:
        if self.best_bid is not None and self.best_ask is not None:
            return max(0.0, self.best_ask - self.best_bid)
        return 0.0

    @property
    def spread_bps(self) -> float:
        mid = self.mid_price
        if mid and mid > 0:
            return (self.spread / mid) * 10000.0
        return 0.0

    def total_bid_depth(self) -> float:
        return sum(qty for _, qty in self.bids)

    def total_ask_depth(self) -> float:
        return sum(qty for _, qty in self.asks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset": self.asset,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "mid_price": self.mid_price,
            "spread": round(self.spread, 4),
            "spread_bps": round(self.spread_bps, 2),
            "total_bid_depth": self.total_bid_depth(),
            "total_ask_depth": self.total_ask_depth()
        }
