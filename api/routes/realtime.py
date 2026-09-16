"""
Real-Time Paper Trading & System Monitoring API Routes
Provides REST endpoints for session status, signals, portfolio mark-to-market, risk gate, kill switch, and session control.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.realtime.scheduler.session_runner import PaperTradingSession
from src.realtime.replay.replay_engine import RealtimeReplayEngine

router = APIRouter(prefix="/realtime", tags=["Real-Time Paper Trading & Monitoring"])

# Active singleton paper session
global_session = PaperTradingSession()


@router.get("/status")
def get_session_status():
    return {
        "status": "success",
        "session_id": global_session.session_id,
        "session_status": global_session.status,
        "kill_switch": global_session.kill_switch.get_status(),
        "health": global_session.health_monitor.get_health_status(),
        "market_calendar": global_session.calendar.get_session_status()
    }


@router.get("/signals")
def get_realtime_signals():
    return {
        "status": "success",
        "signals": list(global_session.signal_engine.last_signals.values())
    }


@router.get("/portfolio")
def get_realtime_portfolio():
    return {
        "status": "success",
        "session_id": global_session.session_id,
        "equity": global_session.equity,
        "cash": global_session.cash,
        "gross_exposure": sum(p["weight"] for p in global_session.positions.values()),
        "net_exposure": sum(p["weight"] for p in global_session.positions.values()),
        "unrealized_pnl": sum(p["unrealized_pnl"] for p in global_session.positions.values())
    }


@router.get("/positions")
def get_realtime_positions():
    return {
        "status": "success",
        "positions": list(global_session.positions.values())
    }


@router.get("/orders")
def get_realtime_orders():
    return {
        "status": "success",
        "orders": global_session.execution_engine.get_orders()
    }


@router.get("/fills")
def get_realtime_fills():
    return {
        "status": "success",
        "fills": global_session.execution_engine.get_fills()
    }


@router.get("/risk")
def get_realtime_risk():
    return {
        "status": "success",
        "kill_switch": global_session.kill_switch.get_status(),
        "risk_limits": {
            "max_position_pct": global_session.risk_gate.max_position_pct,
            "max_gross_exposure": global_session.risk_gate.max_gross_exposure,
            "max_drawdown_pct": global_session.risk_gate.max_drawdown_pct
        }
    }


@router.get("/events")
def get_realtime_events():
    return {
        "status": "success",
        "events": global_session.event_log
    }


@router.get("/alerts")
def get_realtime_alerts(severity: Optional[str] = None):
    return {
        "status": "success",
        "alerts": global_session.alert_engine.get_alerts(severity_filter=severity)
    }


@router.post("/start")
def start_realtime_session():
    res = global_session.start_session()
    return {"status": "success", "session": res}


@router.post("/stop")
def stop_realtime_session():
    res = global_session.stop_session()
    return {"status": "success", "session": res}


@router.post("/pause")
def pause_realtime_session():
    global_session.status = "PAUSED"
    return {"status": "success", "session_status": "PAUSED"}


@router.post("/resume")
def resume_realtime_session():
    if not global_session.kill_switch.is_active:
        global_session.status = "RUNNING"
    return {"status": "success", "session_status": global_session.status}


class KillSwitchRequest(BaseModel):
    action: str = "activate"  # activate | deactivate
    reason: str = "Manual API kill switch request"


@router.post("/kill-switch")
def toggle_kill_switch(req: KillSwitchRequest):
    if req.action.lower() == "activate":
        global_session.kill_switch.activate(req.reason)
    else:
        try:
            global_session.kill_switch.deactivate()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "kill_switch": global_session.kill_switch.get_status()}
