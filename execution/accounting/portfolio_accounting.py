"""
Portfolio Accounting Engine for processing fills, updating cash, positions, PnL, and ledger entries.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from execution.fills.fill_engine import Fill
from execution.orders.order_types import OrderSide


class PortfolioAccounting:
    """Tracks position inventory, cash balance, PnL, and execution ledger entries."""

    def __init__(self, initial_cash: float = 100000.0, borrow_rate_annual: float = 0.02):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.borrow_rate_annual = borrow_rate_annual
        self.positions: Dict[str, Dict[str, float]] = {}  # {asset: {"quantity": qty, "avg_price": price}}
        self.realized_pnl = 0.0
        self.ledger: List[Dict[str, Any]] = []

    def process_fill(self, fill: Fill, market_price: Optional[float] = None) -> Dict[str, Any]:
        """Updates positions and cash ledger given an execution fill."""
        asset = fill.asset
        qty = fill.quantity
        price = fill.fill_price
        side = fill.side
        fees = fill.fees

        pos = self.positions.get(asset, {"quantity": 0.0, "avg_price": 0.0})
        curr_qty = pos["quantity"]
        curr_price = pos["avg_price"]

        realized_trade_pnl = 0.0

        if side == OrderSide.BUY:
            cost = (qty * price) + fees
            self.cash -= cost
            new_qty = curr_qty + qty
            if new_qty > 0:
                new_avg_price = ((curr_qty * curr_price) + (qty * price)) / new_qty
            else:
                new_avg_price = 0.0
            self.positions[asset] = {"quantity": new_qty, "avg_price": new_avg_price}

        elif side == OrderSide.SELL:
            proceeds = (qty * price) - fees
            self.cash += proceeds
            if curr_qty > 0:
                closed_qty = min(curr_qty, qty)
                realized_trade_pnl = (price - curr_price) * closed_qty - fees
                self.realized_pnl += realized_trade_pnl
            new_qty = curr_qty - qty
            new_avg_price = curr_price if new_qty > 0 else 0.0
            self.positions[asset] = {"quantity": new_qty, "avg_price": new_avg_price}

        elif side == OrderSide.SHORT:
            proceeds = (qty * price) - fees
            self.cash += proceeds
            new_qty = curr_qty - qty  # negative quantity for short
            new_avg_price = price
            self.positions[asset] = {"quantity": new_qty, "avg_price": new_avg_price}

        elif side == OrderSide.COVER:
            cost = (qty * price) + fees
            self.cash -= cost
            if curr_qty < 0:
                closed_qty = min(abs(curr_qty), qty)
                realized_trade_pnl = (curr_price - price) * closed_qty - fees
                self.realized_pnl += realized_trade_pnl
            new_qty = curr_qty + qty
            new_avg_price = curr_price if new_qty < 0 else 0.0
            self.positions[asset] = {"quantity": new_qty, "avg_price": new_avg_price}

        entry = {
            "timestamp": fill.timestamp,
            "fill_id": fill.fill_id,
            "order_id": fill.order_id,
            "asset": asset,
            "side": fill.side.value if hasattr(fill.side, "value") else str(fill.side),
            "quantity": qty,
            "price": price,
            "fees": fees,
            "cash_after": round(self.cash, 2),
            "position_after": round(self.positions[asset]["quantity"], 4),
            "realized_pnl": round(realized_trade_pnl, 2)
        }
        self.ledger.append(entry)
        return entry

    def calculate_valuation(self, market_prices: Dict[str, float]) -> Dict[str, Any]:
        """Calculates total portfolio value, unrealized PnL, and position breakdown."""
        positions_val = 0.0
        unrealized_pnl = 0.0
        pos_breakdown = {}

        for asset, pos in self.positions.items():
            qty = pos["quantity"]
            avg_p = pos["avg_price"]
            curr_p = market_prices.get(asset, avg_p)
            val = qty * curr_p
            positions_val += val
            u_pnl = (curr_p - avg_p) * qty
            unrealized_pnl += u_pnl
            pos_breakdown[asset] = {
                "quantity": round(qty, 4),
                "avg_price": round(avg_p, 4),
                "market_price": round(curr_p, 4),
                "market_value": round(val, 2),
                "unrealized_pnl": round(u_pnl, 2)
            }

        total_value = self.cash + positions_val
        return {
            "cash": round(self.cash, 2),
            "positions_value": round(positions_val, 2),
            "total_portfolio_value": round(total_value, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "total_pnl": round(self.realized_pnl + unrealized_pnl, 2),
            "positions": pos_breakdown
        }
