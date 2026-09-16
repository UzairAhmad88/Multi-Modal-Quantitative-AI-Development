"""
Trade Ledger & Portfolio Accounting Module
Maintains active positions, cash balance, realized/unrealized P&L, and portfolio equity snapshots.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import pandas as pd


class TradeLedger:
    """Quantitative Trade Ledger & Real-Time Portfolio Accountant."""

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}  # symbol -> {quantity, avg_cost}
        self.realized_pnl: float = 0.0
        self.total_commission: float = 0.0
        self.snapshots: List[Dict[str, Any]] = []

    def record_fill(self, fill: Dict[str, Any]):
        """
        Update positions, cash, and P&L based on executed order fill.
        """
        sym = fill["symbol"].upper()
        side = fill["side"].upper()
        qty = float(fill["quantity"])
        price = float(fill["fill_price"])
        comm = float(fill.get("commission", 0.0))

        self.total_commission += comm
        self.cash -= comm

        curr_pos = self.positions.get(sym, {"quantity": 0.0, "avg_cost": 0.0})
        curr_qty = curr_pos["quantity"]
        curr_cost = curr_pos["avg_cost"]

        if side == "BUY":
            cost_basis = curr_qty * curr_cost + qty * price
            new_qty = curr_qty + qty
            new_cost = cost_basis / new_qty if new_qty > 0 else 0.0
            self.cash -= (qty * price)
            self.positions[sym] = {"quantity": new_qty, "avg_cost": new_cost}
        elif side == "SELL":
            pnl = (price - curr_cost) * qty
            self.realized_pnl += pnl
            self.cash += (qty * price)
            new_qty = curr_qty - qty
            if new_qty <= 1e-6:
                self.positions.pop(sym, None)
            else:
                self.positions[sym] = {"quantity": new_qty, "avg_cost": curr_cost}

    def take_snapshot(self, market_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate current equity, unrealized P&L, gross/net exposure, and record snapshot.
        """
        unrealized = 0.0
        position_values = {}

        for sym, pos in self.positions.items():
            qty = pos["quantity"]
            avg_cost = pos["avg_cost"]
            mkt_p = market_prices.get(sym, avg_cost)
            val = qty * mkt_p
            position_values[sym] = val
            unrealized += (mkt_p - avg_cost) * qty

        total_position_val = sum(position_values.values())
        equity = self.cash + total_position_val
        gross_exposure = total_position_val / equity if equity > 0 else 0.0

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cash": round(self.cash, 2),
            "equity": round(equity, 2),
            "position_value": round(total_position_val, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "unrealized_pnl": round(unrealized, 2),
            "total_pnl": round(self.realized_pnl + unrealized, 2),
            "total_commission": round(self.total_commission, 2),
            "gross_exposure": round(gross_exposure, 4),
            "active_positions_count": len(self.positions),
        }
        self.snapshots.append(snapshot)
        return snapshot
