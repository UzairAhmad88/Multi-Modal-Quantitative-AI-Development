"""
Streamlit Page 17: Real-Time Paper Trading Command Center
Monitors real-time paper session status, market calendar, live alpha signals, paper portfolio mark-to-market, order execution blotter, risk gate status, and kill switch.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.realtime.scheduler.session_runner import PaperTradingSession
from src.realtime.replay.replay_engine import RealtimeReplayEngine
from src.realtime.monitoring.health import SystemHealthMonitor

st.set_page_config(page_title="Real-Time Paper Trading", page_icon="📡", layout="wide")

st.title("📡 Real-Time Paper Trading & Execution Command Center")
st.caption("Institutional Paper Execution Engine, Real-Time Risk Gate & Health Monitoring")

# Initialize session
session = PaperTradingSession()

# System Header Status Metrics
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Trading Mode", "PAPER TRADING ONLY", help="REAL-MONEY TRADING IS DISABLED")
with col2:
    st.metric("Session Status", session.status)
with col3:
    st.metric("Portfolio Equity", f"${session.equity:,.2f}")
with col4:
    st.metric("Cash Balance", f"${session.cash:,.2f}")
with col5:
    ks_status = session.kill_switch.get_status()
    st.metric("Kill Switch", ks_status["status"], delta="OPERATIONAL" if not ks_status["kill_switch_active"] else "-HALTED")

st.markdown("---")

# Control Buttons & Kill Switch
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
with ctrl_col1:
    if st.button("▶️ Start Session"):
        res = session.start_session()
        st.success(f"Session Started: {res.get('session_id')}")
        st.rerun()
with ctrl_col2:
    if st.button("⏹️ Stop Session"):
        res = session.stop_session()
        st.warning("Session Stopped.")
        st.rerun()
with ctrl_col3:
    if st.button("🚨 TRIGGER KILL SWITCH"):
        session.kill_switch.activate("Operator emergency trigger from Dashboard UI")
        st.error("KILL SWITCH ACTIVATED! All new orders halted.")
        st.rerun()
with ctrl_col4:
    if st.button("🔄 Reset Kill Switch"):
        try:
            session.kill_switch.deactivate()
            st.success("Kill switch reset to OPERATIONAL.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Live Signals & Portfolio", 
    "📑 Order Execution Blotter", 
    "🛡️ Risk Gate & Health", 
    "🔁 Historical Data Replay", 
    "📋 Session Logs"
])

# 1. LIVE SIGNALS & PORTFOLIO
with tab1:
    st.subheader("Live Market Signals & Mark-to-Market Portfolio")
    sig_list = list(session.signal_engine.last_signals.values())
    if sig_list:
        st.write("#### Active Multimodal Alpha Signals")
        st.dataframe(pd.DataFrame(sig_list), use_container_width=True)
    else:
        st.info("No active signals generated yet in current session.")

    st.markdown("---")
    st.write("#### Open Paper Positions")
    pos_list = list(session.positions.values())
    if pos_list:
        st.dataframe(pd.DataFrame(pos_list), use_container_width=True)
    else:
        st.info("No open paper positions.")

# 2. ORDER EXECUTION BLOTTER
with tab2:
    st.subheader("Simulated Order Execution Blotter")
    orders = session.execution_engine.get_fills()
    if orders:
        st.dataframe(pd.DataFrame(orders), use_container_width=True)
    else:
        st.info("No orders executed yet in this session.")

# 3. RISK GATE & HEALTH
with tab3:
    st.subheader("Pre-Trade Risk Gate & System Health")
    health = session.health_monitor.get_health_status()
    st.json(health)

    st.markdown("### Active Risk Gate Rules")
    st.write(f"- **Max Single Position**: {session.risk_gate.max_position_pct:.0%}")
    st.write(f"- **Max Gross Exposure**: {session.risk_gate.max_gross_exposure:.0%}")
    st.write(f"- **Max Portfolio Drawdown**: {session.risk_gate.max_drawdown_pct:.0%}")

# 4. HISTORICAL REPLAY
with tab4:
    st.subheader("High-Speed Market Data Replay Simulation")
    st.markdown("Replay historical market data through the real-time pipeline at accelerated speeds.")

    rep_col1, rep_col2 = st.columns(2)
    with rep_col1:
        selected_speed = st.selectbox("Replay Speed Multiplier:", [1, 10, 100])
    with rep_col2:
        if st.button("▶️ Execute 10x Historical Replay Simulation"):
            with st.spinner("Executing accelerated replay simulation..."):
                engine = RealtimeReplayEngine(speed_multiplier=selected_speed)
                res = engine.run_replay(symbols=["AAPL", "MSFT", "NVDA"], demo=True)
                st.success(f"Replay Session Completed: {res.get('session_id')}")
                st.json(res)

# 5. SESSION LOGS
with tab5:
    st.subheader("Real-Time Event & Audit Log")
    if session.event_log:
        st.dataframe(pd.DataFrame(session.event_log), use_container_width=True)
    else:
        st.info("Event log is empty.")
