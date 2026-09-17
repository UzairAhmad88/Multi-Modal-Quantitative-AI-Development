"""
Real-Time Trading Session Manager Module.
Orchestrates multi-environment execution (PAPER, SHADOW, SANDBOX, LIVE), broker abstraction,
order state machine, risk gates, position reconciliation, and audit logging.
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
from src.realtime.monitoring.health import SystemHealthMonitor
from src.realtime.alerts.engine import AlertEngine

# Execution & Safety Imports
from src.execution.broker.base import BrokerInterface
from src.execution.broker.paper import PaperBroker
from src.execution.broker.sandbox import SandboxBroker
from src.execution.broker.adapters.shadow import ShadowBroker
from src.execution.broker.adapters.alpaca_adapter import AlpacaBrokerAdapter
from src.execution.reconciliation.engine import ReconciliationEngine, ReconciliationResult
from src.execution.safety.environment import SafetyGuard, ExecutionEnvironment
from src.execution.orders.order_lineage import LineageTracker, OrderLineageRecord


class PaperTradingSession:
    """Quantitative Real-Time Session Manager with Broker Abstraction & Safety Gates."""

    def __init__(
        self,
        initial_capital: float = 100000.0,
        broker_override: Optional[BrokerInterface] = None,
        mode_env_var: str = "TRADING_MODE"
    ):
        self.env = SafetyGuard.get_current_environment()
        self.session_id = f"SESSION-{self.env.value}-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.equity = initial_capital
        self.status = "INITIALIZING"

        # Pipelines
        self.calendar = MarketCalendar()
        self.validator = DataValidator()
        self.feature_engine = OnlineFeatureEngine()
        self.signal_engine = RealtimeSignalEngine()
        self.rebalancer = PortfolioRebalancer()
        self.risk_gate = RealtimeRiskGate()
        self.kill_switch = TradingKillSwitch(mode_env_var=mode_env_var)
        self.health_monitor = SystemHealthMonitor()
        self.alert_engine = AlertEngine()
        self.reconciliation_engine = ReconciliationEngine()
        self.lineage_tracker = LineageTracker()

        # Select Broker based on Environment
        if broker_override:
            self.broker = broker_override
        else:
            self.broker = self._initialize_broker()

        self.broker.connect()

        self.positions: Dict[str, Dict[str, Any]] = {}
        self.event_log: List[Dict[str, Any]] = []

    def _initialize_broker(self) -> BrokerInterface:
        """Instantiate appropriate broker adapter based on SafetyGuard configuration."""
        if self.env == ExecutionEnvironment.LIVE:
            permitted, reason = SafetyGuard.verify_live_execution_permitted()
            if not permitted:
                self.kill_switch.activate(f"LIVE_TRADING_BLOCKED: {reason}")
                return PaperBroker(initial_capital=self.initial_capital)
            return AlpacaBrokerAdapter(paper=False)
        elif self.env == ExecutionEnvironment.SANDBOX:
            return SandboxBroker(initial_cash=self.initial_capital)
        elif self.env == ExecutionEnvironment.SHADOW:
            return ShadowBroker(initial_cash=self.initial_capital)
        else:
            # Default to PaperBroker
            return PaperBroker(initial_capital=self.initial_capital)

    def start_session(self) -> Dict[str, Any]:
        """Initialize session state, perform broker reconciliation, and warm-up checks."""
        if self.kill_switch.is_active:
            self.status = "HALTED"
            return {"status": "HALTED", "reason": self.kill_switch.reason}

        # Startup Reconciliation Check
        if self.broker.is_connected():
            reconcile_res = self.reconciliation_engine.reconcile(
                broker=self.broker,
                local_cash=self.cash,
                local_positions=self.positions
            )
            if not reconcile_res.is_reconciled and self.env == ExecutionEnvironment.LIVE:
                self.kill_switch.activate(f"STARTUP_RECONCILIATION_FAILED: {reconcile_res.status_summary}")
                self.status = "HALTED"
                return {"status": "HALTED", "reason": reconcile_res.status_summary, "reconciliation": reconcile_res.to_dict()}

        self.status = "RUNNING"
        self._log_event("SESSION_STARTED", "INFO", f"Trading session '{self.session_id}' initialized in environment '{self.env.value}'")
        return {
            "status": "RUNNING",
            "session_id": self.session_id,
            "environment": self.env.value,
            "cash": self.cash,
            "equity": self.equity,
            "broker_connected": self.broker.is_connected()
        }

    def process_tick_or_bar(self, symbol: str, bar: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process single incoming market bar:
        Validation ➔ Feature Calc ➔ Signal ➔ Rebalance ➔ Risk Gate ➔ Broker Order ➔ Lineage Log ➔ Reconciliation.
        """
        if self.kill_switch.is_active:
            return {"status": "HALTED", "reason": self.kill_switch.reason}

        # Update paper broker price if applicable
        if isinstance(self.broker, PaperBroker):
            self.broker.update_market_price(symbol, float(bar.get("close", 150.0)))

        # 1. Data Validation
        val_res = self.validator.validate_record(bar)
        if not val_res["is_valid"]:
            self.alert_engine.emit_alert("DATA_STALE_OR_INVALID", val_res["reason"], "WARNING", "DATA")
            if val_res["status"] == "STALE":
                self.kill_switch.activate(f"Data feed stale for symbol {symbol}")
            return {"status": "DATA_REJECTED", "validation": val_res}

        # 2. Online Feature Calculation
        df_feats = self.feature_engine.update_and_compute(symbol, bar)
        latest_feat = self.feature_engine.get_latest_feature_vector(symbol) or bar

        # 3. Signal Inference
        sig = self.signal_engine.generate_signal(symbol, latest_feat, timestamp=str(bar.get("timestamp")))
        self._log_event("SIGNAL_GENERATED", "INFO", f"Signal {sig['direction']} for {symbol} (alpha={sig.get('composite_alpha', 0.0)})")

        # 4. Portfolio Rebalancing
        portfolio_state = {
            "equity": self.equity,
            "cash": self.cash,
            "positions": self.positions,
            "drawdown": (self.initial_capital - self.equity) / self.initial_capital if self.equity < self.initial_capital else 0.0
        }

        proposed_trades = self.rebalancer.compute_rebalance([sig], portfolio_state)
        executed_orders = []

        # 5. Pre-Trade Risk Gate & 6. Broker Order Execution
        for trade in proposed_trades:
            risk_decision = self.risk_gate.validate_proposed_trade(trade, portfolio_state, is_data_stale=False)
            self._log_event("RISK_GATE_DECISION", "INFO", f"Risk Gate: {risk_decision['decision']} for {symbol}")

            if risk_decision["decision"] in ["APPROVED", "REDUCED"]:
                qty = risk_decision["approved_quantity"]
                if qty > 0:
                    # Submit Order via Abstract Broker Interface
                    order_rec = self.broker.submit_order(
                        symbol=trade["symbol"],
                        side=trade["side"],
                        quantity=qty,
                        order_type="MARKET",
                        limit_price=trade.get("price"),
                        signal_id=sig["signal_id"],
                        idempotency_key=f"IDEMP-{sig['signal_id']}"
                    )
                    executed_orders.append(order_rec)

                    # Lineage Tracking
                    lineage_rec = OrderLineageRecord(
                        internal_order_id=order_rec.get("order_id", f"ORD-{uuid.uuid4().hex[:6]}"),
                        signal_id=sig["signal_id"],
                        model_id=sig.get("model_id", "MMQAI-MODEL"),
                        model_version="v2.5",
                        environment=self.env.value,
                        symbol=symbol,
                        side=trade["side"],
                        quantity=qty,
                        alpha_score=sig.get("composite_alpha", 0.0),
                        risk_decision=risk_decision["decision"],
                        risk_reason=risk_decision["reason"],
                        broker_order_id=order_rec.get("broker_order_id"),
                        broker_name=self.broker.__class__.__name__,
                        status=order_rec.get("status", "FILLED"),
                        fill_id=order_rec.get("fill_id"),
                        fill_price=order_rec.get("fill_price"),
                        filled_quantity=order_rec.get("quantity", qty)
                    )
                    self.lineage_tracker.register_lineage(lineage_rec)

        # 7. Update Account Snapshot from Authoritative Broker
        acc_info = self.broker.get_account()
        self.cash = acc_info.cash
        self.equity = acc_info.equity

        pos_dict = self.broker.get_positions()
        self.positions = {
            sym: {
                "symbol": p.symbol,
                "quantity": p.quantity,
                "avg_price": p.avg_price,
                "market_price": p.market_price,
                "market_value": p.market_value,
                "unrealized_pnl": p.unrealized_pnl,
                "weight": p.weight
            }
            for sym, p in pos_dict.items()
        }

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

    def trigger_reconciliation(self) -> ReconciliationResult:
        """Execute manual/periodic reconciliation pass."""
        return self.reconciliation_engine.reconcile(
            broker=self.broker,
            local_cash=self.cash,
            local_positions=self.positions
        )

    def _log_event(self, event_type: str, severity: str, message: str):
        self.event_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "environment": self.env.value,
            "event_type": event_type,
            "severity": severity,
            "message": message
        })

    def stop_session(self) -> Dict[str, Any]:
        """Gracefully stop session and persist final state."""
        self.status = "STOPPED"
        self._log_event("SESSION_STOPPED", "INFO", "Trading session gracefully shut down")
        self.broker.disconnect()
        return {
            "status": "STOPPED",
            "session_id": self.session_id,
            "environment": self.env.value,
            "final_equity": self.equity,
            "final_cash": self.cash,
            "total_trades": len(self.broker.get_fills())
        }
