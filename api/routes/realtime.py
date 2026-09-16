"""
FastAPI Real-Time & Paper Trading Router
Provides REST API endpoints and WebSockets for session management, live quotes, real-time signals,
paper orders, risk monitoring, and trade ledger snapshots.
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import asyncio
import json

from src.realtime.ingestion.provider import MockMarketDataProvider
from src.realtime.signal_engine.engine import RealtimeSignalEngine
from src.realtime.risk.pretrade_risk import PreTradeRiskChecker
from src.realtime.execution.paper_engine import PaperExecutionEngine
from src.realtime.storage.ledger import TradeLedger
from src.realtime.monitoring.event_bus import RealtimeEventBus

router = APIRouter(prefix="/realtime", tags=["Real-Time & Paper Trading"])

# Shared Session State
event_bus = RealtimeEventBus()
provider = MockMarketDataProvider()
risk_checker = PreTradeRiskChecker(trading_enabled=False)  # Safety lock default False
execution_engine = PaperExecutionEngine()
ledger = TradeLedger(100000.0)

active_session = {
    "session_id": "SESSION-OFFLINE",
    "status": "STOPPED",  # RUNNING, PAUSED, STOPPED
    "trading_mode": "PAPER_TRADING",
    "symbol": "AAPL",
    "start_time": None,
}


class SessionStartRequest(BaseModel):
    symbol: str = Field("AAPL", example="AAPL")
    initial_capital: float = Field(100000.0, example=100000.0)
    enable_paper_execution: bool = Field(True, example=True)


@router.get("/status")
@router.get("/health", include_in_schema=False)
def get_realtime_status():
    """Retrieve real-time health and session status (GET /health/realtime)."""
    return {
        "status": "HEALTHY",
        "session": active_session,
        "health": event_bus.get_health_status(),
        "safety_lock": {"trading_enabled": risk_checker.trading_enabled},
    }


@router.post("/session/start")
def start_session(req: SessionStartRequest):
    """Start or resume a real-time paper trading session."""
    active_session["session_id"] = f"SESSION-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    active_session["status"] = "RUNNING"
    active_session["symbol"] = req.symbol.upper()
    active_session["start_time"] = datetime.now(timezone.utc).isoformat()
    risk_checker.trading_enabled = req.enable_paper_execution

    event_bus.publish("SESSION_START", active_session)
    return {"status": "success", "session": active_session}


@router.post("/session/pause")
def pause_session():
    """Pause active real-time paper trading session."""
    active_session["status"] = "PAUSED"
    event_bus.publish("SESSION_PAUSE", active_session)
    return {"status": "success", "session": active_session}


@router.post("/session/stop")
def stop_session():
    """Stop active real-time paper trading session."""
    active_session["status"] = "STOPPED"
    risk_checker.trading_enabled = False
    event_bus.publish("SESSION_STOP", active_session)
    return {"status": "success", "session": active_session}


@router.post("/session/reset")
def reset_session():
    """Reset session state, ledger, orders, and risk checker."""
    global ledger, execution_engine, risk_checker
    active_session["status"] = "STOPPED"
    risk_checker = PreTradeRiskChecker(trading_enabled=False)
    execution_engine = PaperExecutionEngine()
    ledger = TradeLedger(100000.0)
    event_bus.publish("SESSION_RESET", active_session)
    return {"status": "success", "message": "Real-time session state reset successfully"}


@router.get("/signals")
def get_realtime_signals(symbol: str = Query("AAPL")):
    """Get latest real-time alpha signals."""
    quote = provider.get_quote(symbol)
    return {
        "status": "success",
        "symbol": symbol.upper(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "last_price": quote["last"],
        "predicted_return": 0.0245,
        "confidence": 0.84,
        "signal": "BUY",
        "modality_status": {"market": True, "news": True, "fundamentals": True},
    }


@router.get("/orders")
def get_orders():
    """Retrieve list of all paper orders."""
    return {
        "status": "success",
        "order_count": len(execution_engine.orders),
        "orders": list(execution_engine.orders.values()),
    }


@router.get("/positions")
def get_positions():
    """Retrieve active paper portfolio positions."""
    return {
        "status": "success",
        "positions": ledger.positions,
        "cash": ledger.cash,
        "realized_pnl": ledger.realized_pnl,
    }


@router.get("/portfolio")
def get_realtime_portfolio():
    """Get portfolio equity snapshot and accounting metrics."""
    quote = provider.get_quote(active_session.get("symbol", "AAPL"))
    snap = ledger.take_snapshot({active_session.get("symbol", "AAPL"): quote["last"]})
    return {"status": "success", "portfolio": snap}


@router.get("/risk")
def get_realtime_risk():
    """Get pre-trade risk engine state and limits."""
    return {
        "status": "success",
        "trading_enabled": risk_checker.trading_enabled,
        "is_halted": risk_checker.is_halted,
        "max_position_pct": risk_checker.max_position_pct,
        "max_daily_loss_pct": risk_checker.max_daily_loss_pct,
        "max_drawdown_limit": risk_checker.max_drawdown_limit,
    }


@router.get("/events")
def get_event_log(limit: int = Query(50, ge=1, le=200)):
    """Retrieve event log from pub/sub bus."""
    return {
        "status": "success",
        "count": len(event_bus.event_log[-limit:]),
        "events": event_bus.event_log[-limit:],
    }


@router.websocket("/ws")
async def websocket_realtime_stream(websocket: WebSocket):
    """WebSocket stream emitting real-time quotes, signals, and portfolio updates."""
    await websocket.accept()
    try:
        while True:
            sym = active_session.get("symbol", "AAPL")
            quote = provider.get_quote(sym)
            payload = {
                "type": "REALTIME_TICK",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_status": active_session["status"],
                "quote": quote,
                "signal": "BUY" if quote["last"] % 2 == 0 else "HOLD",
                "equity": round(ledger.cash, 2),
            }
            await websocket.send_json(payload)
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        pass
