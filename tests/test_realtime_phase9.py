"""
Test Suite for Phase 9 Real-Time Paper Trading & Monitoring Platform
Tests Market Calendar, Data Validation, Online Feature Engine, Realtime Signal Engine,
Portfolio Rebalancer, Pre-Trade Risk Gate, Kill Switch, Paper Execution Engine,
System Health Monitor, Alert Engine, Session Runner, and Replay Engine.
"""

from datetime import datetime, timezone, timedelta
import pytest
import pandas as pd

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
from src.realtime.scheduler.session_runner import PaperTradingSession
from src.realtime.replay.replay_engine import RealtimeReplayEngine


def test_market_calendar():
    cal = MarketCalendar()
    # Wednesday 15:00 UTC (Market open)
    dt_open = datetime(2023, 5, 10, 15, 0, tzinfo=timezone.utc)
    assert cal.is_market_open(dt_open) == True

    # Sunday (Market closed)
    dt_sun = datetime(2023, 5, 14, 15, 0, tzinfo=timezone.utc)
    assert cal.is_market_open(dt_sun) == False

    status = cal.get_session_status(dt_open)
    assert status["status"] == "OPEN"


def test_data_validator():
    val = DataValidator(max_staleness_sec=300.0)
    now = datetime.now(timezone.utc)

    # Valid record
    rec_valid = {"symbol": "AAPL", "timestamp": now.isoformat(), "close": 150.0, "volume": 1000}
    res_valid = val.validate_record(rec_valid, current_time=now)
    assert res_valid["is_valid"] == True

    # Duplicate record
    res_dup = val.validate_record(rec_valid, current_time=now)
    assert res_dup["is_valid"] == False
    assert res_dup["status"] == "DUPLICATE"

    # Stale record
    stale_time = now - timedelta(seconds=500)
    rec_stale = {"symbol": "MSFT", "timestamp": stale_time.isoformat(), "close": 250.0, "volume": 1200}
    res_stale = val.validate_record(rec_stale, current_time=now)
    assert res_stale["is_valid"] == False
    assert res_stale["status"] == "STALE"


def test_online_feature_engine():
    engine = OnlineFeatureEngine(lookback_window=10)
    bar = {"open": 150.0, "high": 155.0, "low": 149.0, "close": 152.0, "volume": 1000}
    df_feats = engine.update_and_compute("AAPL", bar)
    assert len(df_feats) >= 1
    assert "close" in df_feats.columns

    vec = engine.get_latest_feature_vector("AAPL")
    assert vec is not None
    assert vec["close"] == 152.0

    # Parity test
    parity = engine.verify_parity(df_feats, df_feats)
    assert parity["is_parity"] == True


def test_realtime_signal_engine():
    sig_engine = RealtimeSignalEngine(min_confidence=0.50, long_threshold=0.005)
    feat = {"return_1d": 0.05, "rsi": 65.0}

    sig = sig_engine.generate_signal("AAPL", feat, news_sentiment=0.8)
    assert sig["symbol"] == "AAPL"
    assert sig["direction"] in ["BUY", "STRONG BUY"]
    assert sig["confidence"] >= 0.50

    # Debouncing check
    sig2 = sig_engine.generate_signal("AAPL", feat, news_sentiment=0.8)
    assert sig2["is_debounced"] == True


def test_portfolio_rebalancer():
    rebalancer = PortfolioRebalancer(max_asset_weight=0.25)
    signals = [{"symbol": "AAPL", "direction": "STRONG BUY", "price": 150.0, "signal_id": "SIG-1"}]
    portfolio = {"equity": 100000.0, "positions": {}}

    trades = rebalancer.compute_rebalance(signals, portfolio)
    assert len(trades) == 1
    assert trades[0]["symbol"] == "AAPL"
    assert trades[0]["side"] == "BUY"
    assert trades[0]["target_weight"] <= 0.25


def test_realtime_risk_gate():
    gate = RealtimeRiskGate(max_position_pct=0.25, max_drawdown_pct=0.10)
    trade = {
        "symbol": "AAPL",
        "proposed_value": 20000.0,
        "target_weight": 0.20,
        "current_weight": 0.0,
        "quantity": 100.0,
        "price": 150.0
    }
    portfolio = {"equity": 100000.0, "drawdown": 0.02}

    res_appr = gate.validate_proposed_trade(trade, portfolio, is_data_stale=False)
    assert res_appr["decision"] == "APPROVED"

    # Stale data check
    res_stale = gate.validate_proposed_trade(trade, portfolio, is_data_stale=True)
    assert res_stale["decision"] == "REJECTED"

    # Excess position check
    trade_excess = dict(trade)
    trade_excess["target_weight"] = 0.40
    res_red = gate.validate_proposed_trade(trade_excess, portfolio, is_data_stale=False)
    assert res_red["decision"] == "REDUCED"


def test_trading_kill_switch():
    ks = TradingKillSwitch()
    assert ks.get_status()["kill_switch_active"] == False

    ks.activate("Emergency test trigger")
    assert ks.get_status()["kill_switch_active"] == True
    assert ks.get_status()["reason"] == "Emergency test trigger"

    ks.deactivate()
    assert ks.get_status()["kill_switch_active"] == False


def test_paper_execution_engine():
    exec_engine = PaperExecutionEngine(slippage_bps=5.0, commission_bps=10.0)
    order = exec_engine.execute_order("AAPL", "BUY", 10.0, 150.0)

    assert order["status"] == "FILLED"
    assert order["fill_price"] > 150.0  # Slippage added for BUY
    assert order["commission_fee"] > 0.0
    assert len(exec_engine.get_fills()) == 1


def test_system_health_monitor():
    monitor = SystemHealthMonitor()
    assert monitor.is_ready() == True
    assert monitor.is_live() == True

    health = monitor.get_health_status()
    assert health["status"] == "HEALTHY"

    monitor.record_latency("inference", 35.2)
    assert monitor.latency_ms["inference_latency"] == 35.2


def test_alert_engine():
    alerts = AlertEngine(cooldown_sec=60.0)
    a1 = alerts.emit_alert("RISK_BREACH", "Drawdown limit exceeded", "CRITICAL")
    assert a1 is not None
    assert a1["severity"] == "CRITICAL"

    # Cooldown suppression check
    a2 = alerts.emit_alert("RISK_BREACH", "Drawdown limit exceeded", "CRITICAL")
    assert a2 is None


def test_paper_trading_session():
    session = PaperTradingSession(initial_capital=100000.0)
    start_info = session.start_session()
    assert start_info["status"] == "RUNNING"

    now = datetime.now(timezone.utc).isoformat()
    bar = {"symbol": "AAPL", "open": 150.0, "high": 155.0, "low": 149.0, "close": 152.0, "volume": 1000, "timestamp": now}

    res = session.process_tick_or_bar("AAPL", bar)
    assert res["status"] == "PROCESSED"
    assert "signal" in res

    stop_info = session.stop_session()
    assert stop_info["status"] == "STOPPED"


def test_realtime_replay_engine():
    replay = RealtimeReplayEngine(speed_multiplier=10)
    res = replay.run_replay(symbols=["AAPL"], demo=True)
    assert res["status"] == "REPLAY_COMPLETED"
    assert res["processed_bars"] > 0
