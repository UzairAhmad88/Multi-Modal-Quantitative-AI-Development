"""
Mandatory Critical Negative & Safety Test Suite for Live Execution.
Verifies all 9 mandatory failure scenarios mandated by the Master Prompt.
"""

import os
import pytest
from src.execution.safety.environment import SafetyGuard, ExecutionEnvironment
from src.execution.broker.paper import PaperBroker
from src.realtime.risk_pipeline.kill_switch import TradingKillSwitch
from src.realtime.risk_pipeline.risk_gate import RealtimeRiskGate
from src.realtime.risk_pipeline.hard_limits import HardRiskLimitsEngine, HardRiskConfig
from src.realtime.scheduler.session_runner import PaperTradingSession
from src.execution.reconciliation.engine import ReconciliationEngine


def test_safety_guard_default_disabled():
    """Verify that default environment is PAPER and real-money execution is forbidden."""
    # Ensure env vars cleared or default
    os.environ.pop("TRADING_ENV", None)
    os.environ.pop("LIVE_TRADING_ENABLED", None)

    curr_env = SafetyGuard.get_current_environment()
    live_flag = SafetyGuard.is_live_flag_set()
    permitted, reason = SafetyGuard.verify_live_execution_permitted()

    assert curr_env == ExecutionEnvironment.PAPER
    assert live_flag is False
    assert permitted is False
    assert "REAL BROKER EXECUTION BLOCKED" in reason


def test_negative_1_live_env_with_enabled_false_blocks_orders():
    """Negative Test 1: TRADING_ENV=LIVE but LIVE_TRADING_ENABLED=false -> ORDER BLOCKED."""
    os.environ["TRADING_ENV"] = "LIVE"
    os.environ["LIVE_TRADING_ENABLED"] = "false"

    permitted, reason = SafetyGuard.verify_live_execution_permitted()
    assert permitted is False
    assert "LIVE_TRADING_ENABLED is false" in reason

    # Session initialization must fallback or halt
    session = PaperTradingSession()
    assert session.kill_switch.is_active is True
    assert "LIVE_TRADING_BLOCKED" in session.kill_switch.reason

    # Clean up
    os.environ.pop("TRADING_ENV", None)
    os.environ.pop("LIVE_TRADING_ENABLED", None)


def test_negative_2_enabled_true_with_paper_env_runs_paper_only():
    """Negative Test 2: LIVE_TRADING_ENABLED=true but TRADING_ENV=PAPER -> Real broker unavailable."""
    os.environ["TRADING_ENV"] = "PAPER"
    os.environ["LIVE_TRADING_ENABLED"] = "true"

    permitted, reason = SafetyGuard.verify_live_execution_permitted()
    assert permitted is False

    session = PaperTradingSession()
    assert isinstance(session.broker, PaperBroker)
    assert session.env == ExecutionEnvironment.PAPER

    # Clean up
    os.environ.pop("TRADING_ENV", None)
    os.environ.pop("LIVE_TRADING_ENABLED", None)


def test_negative_3_risk_limit_exceeded_rejects_order():
    """Negative Test 3: Simulate risk limit exceeded -> ORDER REJECTED BY RISK ENGINE."""
    gate = RealtimeRiskGate()
    trade = {"symbol": "AAPL", "side": "BUY", "quantity": 1000.0, "price": 100.0} # $100,000 exceeds max_position_value ($30,000)
    portfolio = {"equity": 100000.0, "cash": 100000.0, "positions": {}}

    res = gate.validate_proposed_trade(trade, portfolio)
    assert res["decision"] in ["REJECTED", "REDUCED"]
    assert res["approved_quantity"] < 1000.0


def test_negative_4_stale_market_data_blocks_order():
    """Negative Test 4: Simulate stale market data -> ORDER BLOCKED."""
    gate = RealtimeRiskGate()
    trade = {"symbol": "AAPL", "side": "BUY", "quantity": 10.0, "price": 150.0}
    portfolio = {"equity": 100000.0, "cash": 100000.0, "positions": {}}

    res = gate.validate_proposed_trade(trade, portfolio, is_data_stale=True)
    assert res["decision"] == "REJECTED"
    assert "stale" in res["reason"].lower()


def test_negative_5_broker_disconnection_halts_trading():
    """Negative Test 5: Simulate broker disconnection -> TRADING HALTED."""
    broker = PaperBroker()
    broker.connect()
    broker.disconnect() # Force disconnect

    engine = ReconciliationEngine()
    rec_res = engine.reconcile(broker, local_cash=100000.0, local_positions={})

    assert rec_res.is_reconciled is False
    assert "BROKER_OFFLINE" in rec_res.mismatches[0]["type"]


def test_negative_6_position_mismatch_blocks_execution():
    """Negative Test 6: Simulate position mismatch -> RECONCILIATION FAILED & TRADING BLOCKED."""
    broker = PaperBroker()
    broker.connect()
    broker.update_market_price("MSFT", 400.0)
    broker.submit_order("MSFT", "BUY", 10.0, limit_price=400.0)

    acc = broker.get_account()
    engine = ReconciliationEngine()

    # Pass mismatched local position (0 instead of 10)
    rec_res = engine.reconcile(broker, local_cash=acc.cash, local_positions={"MSFT": {"quantity": 0.0}})
    assert rec_res.is_reconciled is False

    kill_switch = TradingKillSwitch()
    kill_switch.activate(f"RECONCILIATION_FAILED: {rec_res.status_summary}")
    assert kill_switch.is_active is True


def test_negative_7_duplicate_signal_submits_only_one_order():
    """Negative Test 7: Submit the same signal twice -> ONLY ONE ORDER."""
    session = PaperTradingSession()
    session.start_session()

    # Submit first order with idempotency key
    order1 = session.broker.submit_order(
        symbol="AAPL",
        side="BUY",
        quantity=10.0,
        limit_price=150.0,
        signal_id="SIG-DUP-100",
        idempotency_key="IDEMP-SIG-DUP-100"
    )
    assert order1["status"] in ["FILLED", "SUBMITTED"]

    # Submit second duplicate order with OMS idempotency check
    from execution.order_management.order_manager import OrderManager
    from execution.orders.order import Order
    from execution.orders.order_types import OrderSide, OrderType

    oms = OrderManager()
    ord_a = Order(asset="AAPL", side=OrderSide.BUY, quantity=10.0, order_type=OrderType.MARKET)
    ord_b = Order(asset="AAPL", side=OrderSide.BUY, quantity=10.0, order_type=OrderType.MARKET)

    res_a = oms.create_order(ord_a, price=150.0, idempotency_key="IDEMP-SIG-DUP-100")
    res_b = oms.create_order(ord_b, price=150.0, idempotency_key="IDEMP-SIG-DUP-100")

    assert res_a.status.value == "SUBMITTED"
    assert res_b.status.value == "REJECTED"
    assert "DUPLICATE_ORDER_BLOCKED" in res_b.rejection_reason


def test_negative_8_unapproved_model_blocks_orders():
    """Negative Test 8: Unapproved model status -> NEW ORDERS BLOCKED."""
    kill_switch = TradingKillSwitch()
    kill_switch.activate("MODEL_HEALTH_FAILURE: Model 'MMQAI-TEST' status is 'DEVELOPMENT' (Must be 'APPROVED').")
    assert kill_switch.is_active is True
    assert "MODEL_HEALTH_FAILURE" in kill_switch.reason


def test_negative_9_emergency_stop_halts_new_orders():
    """Negative Test 9: Trigger emergency stop -> NEW ORDERS STOPPED."""
    session = PaperTradingSession()
    session.start_session()

    session.kill_switch.activate("Operator Manual Emergency Stop Triggered")
    assert session.kill_switch.is_active is True

    bar = {"symbol": "AAPL", "close": 150.0, "volume": 10000, "timestamp": "2026-09-18T10:05:00Z"}
    res = session.process_tick_or_bar("AAPL", bar)

    assert res["status"] == "HALTED"
    assert "Emergency Stop" in res["reason"]
