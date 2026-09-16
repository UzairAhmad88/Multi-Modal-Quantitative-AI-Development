"""
Deterministic Historical Replay Engine Module
Replays historical data sequentially into the real-time feature, signal, risk, and paper execution engine.
"""

from datetime import datetime, timezone
import time
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from src.realtime.signal_engine.engine import RealtimeSignalEngine
from src.realtime.risk.pretrade_risk import PreTradeRiskChecker
from src.realtime.execution.paper_engine import PaperExecutionEngine
from src.realtime.storage.ledger import TradeLedger


class ReplaySessionEngine:
    """Quantitative Replay Engine for Paper Trading Simulation."""

    def __init__(
        self,
        historical_df: pd.DataFrame,
        symbol: str = "AAPL",
        initial_capital: float = 100000.0,
        replay_speed_multiplier: float = 10.0,
    ):
        self.df = historical_df.copy()
        self.symbol = symbol.upper()
        self.initial_capital = initial_capital
        self.speed_multiplier = replay_speed_multiplier

        self.signal_engine = RealtimeSignalEngine()
        self.risk_checker = PreTradeRiskChecker(trading_enabled=True)  # Enabled for paper replay
        self.execution_engine = PaperExecutionEngine()
        self.ledger = TradeLedger(initial_capital)

        self.session_id = f"REPLAY-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.is_running = False

    def run_replay(self, max_bars: int = 50) -> Dict[str, Any]:
        """
        Execute deterministic replay over historical bars.
        """
        self.is_running = True
        sub_df = self.df.head(max_bars)

        for idx, row in sub_df.iterrows():
            if not self.is_running:
                break

            price = float(row["close"])
            ret = float(row.get("forward_return", row.get("close", 100.0) * 0.001 - 0.0005))
            if np.isnan(ret):
                ret = 0.002

            # 1. Signal Generation
            features = {"close": price, "volume": float(row.get("volume", 1000))}
            sig_res = self.signal_engine.process_features(
                symbol=self.symbol,
                features=features,
                predicted_return=ret,
                confidence=0.75,
            )

            signal = sig_res["signal"]

            # 2. Risk Check & Paper Execution if Actionable Signal
            if signal in ["LONG", "SHORT"]:
                side = "BUY" if signal == "LONG" else "SELL"
                qty = 10.0

                snapshot = self.ledger.take_snapshot({self.symbol: price})
                cash = snapshot["cash"]
                eq = snapshot["equity"]
                pos_dict = {self.symbol: self.ledger.positions.get(self.symbol, {}).get("quantity", 0.0)}

                is_approved, reason = self.risk_checker.check_order(
                    symbol=self.symbol,
                    side=side,
                    quantity=qty,
                    price=price,
                    current_portfolio_value=eq,
                    available_cash=cash,
                    current_positions=pos_dict,
                )

                order = self.execution_engine.create_order(
                    symbol=self.symbol,
                    side=side,
                    quantity=qty,
                    order_type="MARKET",
                )

                executed_order = self.execution_engine.execute_order(
                    order_id=order["order_id"],
                    market_price=price,
                    is_approved=is_approved,
                    rejection_reason=reason,
                )

                if executed_order["status"] == "FILLED":
                    fill = self.execution_engine.fills[-1]
                    self.ledger.record_fill(fill)

            # Record final snapshot for bar
            self.ledger.take_snapshot({self.symbol: price})

        self.is_running = False
        final_snap = self.ledger.snapshots[-1] if self.ledger.snapshots else {}

        return {
            "session_id": self.session_id,
            "total_bars_processed": len(sub_df),
            "total_orders": len(self.execution_engine.orders),
            "total_fills": len(self.execution_engine.fills),
            "final_equity": final_snap.get("equity", self.initial_capital),
            "total_pnl": final_snap.get("total_pnl", 0.0),
        }
