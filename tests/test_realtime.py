"""
Unit & Integration Tests for Phase 6 Real-Time & Paper Trading Engine
Validates market data providers, session management, 15m bar aggregation, signal cooldowns,
pre-trade risk gating, paper execution lifecycle, trade ledger accounting, and replay sessions.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone

from src.realtime.ingestion.provider import MockMarketDataProvider
from src.realtime.ingestion.session import MarketSessionManager
from src.realtime.feature_engine.bar_builder import RealtimeBarBuilder, FeatureParityValidator
from src.realtime.signal_engine.engine import RealtimeSignalEngine
from src.realtime.risk.pretrade_risk import PreTradeRiskChecker
from src.realtime.execution.paper_engine import PaperExecutionEngine
from src.realtime.storage.ledger import TradeLedger
from src.realtime.monitoring.event_bus import RealtimeEventBus
from src.realtime.replay.replay_engine import ReplaySessionEngine


def test_mock_market_provider():
    provider = MockMarketDataProvider(seed=42)
    quote = provider.get_quote("AAPL")
    assert quote["symbol"] == "AAPL"
    assert quote["last"] > 0
    assert "timestamp" in quote

    df_bars = provider.get_bars("AAPL", limit=20)
    assert len(df_bars) == 20
    assert "close" in df_bars.columns


def test_market_session_manager():
    mgr = MarketSessionManager()
    # Wednesday 10:00 AM UTC (Regular trading hours assuming standard session evaluation)
    dt_regular = datetime(2026, 9, 16, 15, 0, tzinfo=timezone.utc)
    assert mgr.get_session_type(dt_regular) == "REGULAR"

    # Saturday
    dt_sat = datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)
    assert mgr.get_session_type(dt_sat) == "CLOSED_WEEKEND"


def test_realtime_bar_builder():
    builder = RealtimeBarBuilder("AAPL", 15)
    bar = None
    for i in range(15):
        tick = {"timestamp": f"2026-09-16T10:00:{i:02d}Z", "last": 150.0 + i, "volume": 100}
        bar = builder.add_tick(tick)

    assert bar is not None
    assert bar["symbol"] == "AAPL"
    assert bar["open"] == 150.0
    assert bar["close"] == 164.0
    assert bar["high"] == 164.0
    assert bar["low"] == 150.0


def test_feature_parity_validator():
    validator = FeatureParityValidator(["momentum", "volatility", "sentiment"])
    df_valid = pd.DataFrame([{"momentum": 0.02, "volatility": 0.15, "sentiment": 0.4}])
    is_ok, issues = validator.validate_features(df_valid)
    assert is_ok
    assert len(issues) == 0

    df_invalid = pd.DataFrame([{"momentum": 0.02}])
    is_ok2, issues2 = validator.validate_features(df_invalid)
    assert not is_ok2


def test_realtime_signal_engine():
    engine = RealtimeSignalEngine(long_threshold=0.01, cooldown_seconds=2)
    res1 = engine.process_features("AAPL", {}, predicted_return=0.02, confidence=0.80)
    assert res1["signal"] == "LONG"

    # Immediate second signal should be skipped due to cooldown
    res2 = engine.process_features("AAPL", {}, predicted_return=0.02, confidence=0.80)
    assert res2["signal"] == "COOLDOWN_SKIP"


def test_pretrade_risk_checker():
    # Test Safety Lock Rejection
    checker_locked = PreTradeRiskChecker(trading_enabled=False)
    ok, msg = checker_locked.check_order("AAPL", "BUY", 10, 150.0, 100000.0, 100000.0, {})
    assert not ok
    assert "SAFETY LOCK" in msg.upper() or "TRADING_ENABLED" in msg

    # Test Allowed Order
    checker = PreTradeRiskChecker(trading_enabled=True)
    ok2, msg2 = checker.check_order("AAPL", "BUY", 10, 150.0, 100000.0, 100000.0, {})
    assert ok2
    assert "APPROVED" in msg2

    # Test Insufficient Cash
    ok3, msg3 = checker.check_order("AAPL", "BUY", 10000, 150.0, 100000.0, 1000.0, {})
    assert not ok3
    assert "INSUFFICIENT CASH" in msg3.upper()


def test_paper_execution_engine():
    engine = PaperExecutionEngine(default_cost_bps=10.0, default_slippage_bps=5.0, simulated_latency_ms=0)
    order = engine.create_order("AAPL", "BUY", 100.0)
    assert order["status"] == "CREATED"

    exec_order = engine.execute_order(order["order_id"], market_price=150.0, is_approved=True)
    assert exec_order["status"] == "FILLED"
    assert exec_order["filled_price"] > 150.0  # Buy slippage adds to price
    assert len(engine.fills) == 1


def test_trade_ledger():
    ledger = TradeLedger(100000.0)
    fill_buy = {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 100.0,
        "fill_price": 150.0,
        "commission": 15.0,
    }
    ledger.record_fill(fill_buy)
    assert "AAPL" in ledger.positions
    assert ledger.positions["AAPL"]["quantity"] == 100.0

    fill_sell = {
        "symbol": "AAPL",
        "side": "SELL",
        "quantity": 100.0,
        "fill_price": 160.0,
        "commission": 16.0,
    }
    ledger.record_fill(fill_sell)
    assert "AAPL" not in ledger.positions
    assert ledger.realized_pnl == pytest.approx(1000.0, 0.01)

    snap = ledger.take_snapshot({"AAPL": 160.0})
    assert snap["equity"] > 100000.0


def test_event_bus():
    bus = RealtimeEventBus()
    received = []
    bus.subscribe("ORDER_FILLED", lambda p: received.append(p))
    bus.publish("ORDER_FILLED", {"order_id": "ORD-123"})

    assert len(received) == 1
    assert received[0]["order_id"] == "ORD-123"

    health = bus.get_health_status()
    assert health["status"] == "HEALTHY"


def test_replay_session_engine():
    dates = pd.date_range("2023-01-01", periods=10, freq="B")
    df_hist = pd.DataFrame({"date": dates, "close": 150.0 + np.arange(10), "volume": 1000})
    replay = ReplaySessionEngine(df_hist, symbol="AAPL", initial_capital=100000.0)

    res = replay.run_replay(max_bars=10)
    assert res["total_bars_processed"] == 10
    assert res["total_orders"] >= 0
