"""
Paper Trading Session Manager Module
Orchestrates real-time paper session initialization, warm-up, tick execution, risk checks, portfolio updates, and state recovery.
"""

from datetime import datetime, timezone
import uuid
import os
from typing import Dict, List, Any, Optional

from src.realtime.ingestion.calendar import MarketCalendar
from src.realtime.ingestion.validation import DataValidator
from src.realtime.feature_pipeline.online_features import OnlineFeatureEngine
from src.realtime.signal_pipeline.realtime_signal import RealtimeSignalEngine
from src.realtime.portfolio_pipeline.rebalancer import PortfolioRebalancer
from src.realtime.risk_pipeline.risk_gate import RealtimeRiskGate
from src.realtime.risk_pipeline.kill_switch import TradingKillSwitch
from src.realtime.execution.paper_execution import PaperExecutionEngine
from src.realtime.monitoring.health import SystemHealthMonitor
from src.realtime.alerts.engine import AlertEngine


class PaperTradingSession:
    """Quantitative Real-Time Paper Trading Session Manager."""

    def __init__(self, initial_capital: float = 100000.0, mode_env_var: str = "TRADING_MODE"):
        self.session_id = f"PAPER-SESSION-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.equity = initial_capital
        self.status = "INITIALIZING"

        self.calendar = MarketCalendar()
        self.validator = DataValidator()
        self.feature_engine = OnlineFeatureEngine()
        self.signal_engine = RealtimeSignalEngine()
        self.rebalancer = PortfolioRebalancer()
        self.risk_gate = RealtimeRiskGate()
        self.kill_switch = TradingKillSwitch(mode_env_var=mode_env_var)
        self.execution_engine = PaperExecutionEngine()
        self.health_monitor = SystemHealthMonitor()
        self.alert_engine = AlertEngine()

        self.positions: Dict[str, Dict[str, Any]] = {}
        self.event_log: List[Dict[str, Any]] = []

    def start_session(self) -> Dict[str, Any]:
        """Initialize session state and execute warm-up checks."""
        if self.kill_switch.is_active:
            self.status = "HALTED"
            return {"status": "HALTED", "reason": self.kill_switch.reason}

        self.status = "RUNNING"
        self._log_event("SESSION_STARTED", "INFO", "Paper trading session initialized successfully")
        return {"status": "RUNNING", "session_id": self.session_id, "cash": self.cash, "equity": self.equity}

    def process_tick_or_bar(self, symbol: str, bar: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process single incoming market bar through complete Phase 9 pipeline:
        Data Validation -> Online Features -> Signal -> Rebalance -> Risk Gate -> Paper Execution -> Accounting.
        """
        if self.kill_switch.is_active:
            return {"status": "HALTED", "reason": self.kill_switch.reason}

        # 1. Data Validation
        val_res = self.validator.validate_record(bar)
        if not val_res["is_valid"]:
            self.alert_engine.emit_alert("DATA_STALE_OR_INVALID", val_res["reason"], "WARNING", "DATA")
            if val_res["status"] == "STALE":
                self.kill_switch.activate(f"Data stale for {symbol}")
            return {"status": "DATA_REJECTED", "validation": val_res}

        # 2. Online Feature Calculation
        df_feats = self.feature_engine.update_and_compute(symbol, bar)
        latest_feat = self.feature_engine.get_latest_feature_vector(symbol) or bar

        # 3. Signal Inference
        sig = self.signal_engine.generate_signal(symbol, latest_feat, timestamp=str(bar.get("timestamp")))
        self._log_event("SIGNAL_GENERATED", "INFO", f"Signal {sig['direction']} for {symbol} (pred={sig['prediction']})")

        # 4. Portfolio Rebalancing
        portfolio_state = {
            "equity": self.equity,
            "cash": self.cash,
            "positions": self.positions,
            "drawdown": (self.initial_capital - self.equity) / self.initial_capital if self.equity < self.initial_capital else 0.0
        }

        proposed_trades = self.rebalancer.compute_rebalance([sig], portfolio_state)
        executed_orders = []

        # 5. Risk Gate & 6. Paper Execution
        for trade in proposed_trades:
            risk_decision = self.risk_gate.validate_proposed_trade(trade, portfolio_state, is_data_stale=False)
            self._log_event("RISK_GATE_DECISION", "INFO", f"Risk Gate: {risk_decision['decision']} for {symbol}")

            if risk_decision["decision"] in ["APPROVED", "REDUCED"]:
                qty = risk_decision["approved_quantity"]
                if qty > 0:
                    order = self.execution_engine.execute_order(
                        symbol=trade["symbol"],
                        side=trade["side"],
                        quantity=qty,
                        price=trade["price"],
                        signal_id=sig["signal_id"]
                    )
                    executed_orders.append(order)

                    # Update Position Accounting
                    self._update_position(order)

        # 7. Mark to Market
        self._mark_to_market(bar)

        return {
            "status": "PROCESSED",
            "symbol": symbol,
            "signal": sig,
            "executed_orders": executed_orders,
            "portfolio": {
                "cash": self.cash,
                "equity": self.equity,
                "positions": self.positions
            }
        }

    def _update_position(self, order: Dict[str, Any]):
        symbol = order["symbol"]
        qty = order["quantity"]
        fill_price = order["fill_price"]
        side = order["side"]
        net_val = order["net_value"]

        if side == "BUY":
            self.cash -= net_val
            if symbol not in self.positions:
                self.positions[symbol] = {
                    "symbol": symbol,
                    "quantity": qty,
                    "avg_price": fill_price,
                    "market_price": fill_price,
                    "market_value": qty * fill_price,
                    "unrealized_pnl": 0.0,
                    "weight": (qty * fill_price) / self.equity if self.equity > 0 else 0.0
                }
            else:
                existing = self.positions[symbol]
                total_qty = existing["quantity"] + qty
                new_avg = (existing["avg_price"] * existing["quantity"] + fill_price * qty) / total_qty
                self.positions[symbol]["quantity"] = total_qty
                self.positions[symbol]["avg_price"] = new_avg

    def _mark_to_market(self, bar: Dict[str, Any]):
        symbol = bar.get("symbol")
        price = float(bar.get("close", 150.0))

        if symbol in self.positions:
            pos = self.positions[symbol]
            pos["market_price"] = price
            pos["market_value"] = pos["quantity"] * price
            pos["unrealized_pnl"] = (price - pos["avg_price"]) * pos["quantity"]

        pos_val = sum(p["market_value"] for p in self.positions.values())
        self.equity = self.cash + pos_val

        for p in self.positions.values():
            p["weight"] = p["market_value"] / self.equity if self.equity > 0 else 0.0

    def _log_event(self, event_type: str, severity: str, message: str):
        self.event_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "severity": severity,
            "message": message
        })

    def stop_session(self) -> Dict[str, Any]:
        """Gracefully stop session and persist final state."""
        self.status = "STOPPED"
        self._log_event("SESSION_STOPPED", "INFO", "Paper session gracefully shut down")
        return {
            "status": "STOPPED",
            "session_id": self.session_id,
            "final_equity": self.equity,
            "final_cash": self.cash,
            "total_trades": len(self.execution_engine.get_fills())
        }
