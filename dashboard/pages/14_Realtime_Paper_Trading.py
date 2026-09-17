"""
QUANT AI: Real-Time Execution Center & Broker Control Terminal
Provides multi-environment trading controls (PAPER, SHADOW, SANDBOX, LIVE),
Broker status indicators, Order Lineage, Reconciliation, and Safety Controls.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timezone

from src.execution.safety.environment import SafetyGuard, ExecutionEnvironment
from src.execution.broker.paper import PaperBroker
from src.realtime.scheduler.session_runner import PaperTradingSession
from src.realtime.ingestion.provider import MockMarketDataProvider

st.set_page_config(page_title="Execution Center - QUANT AI", layout="wide")

st.title("⚡ Quantitative Execution Center & Broker Management")
st.caption("Multi-Environment Order Execution, Broker Abstraction, Lineage Tracking & Risk Controls")

# Session Singleton
if "session" not in st.session_state:
    st.session_state.session = PaperTradingSession(initial_capital=100000.0)

session: PaperTradingSession = st.session_state.session
safety_status = SafetyGuard.get_safety_status()

# Sidebar Environment & Controls
st.sidebar.header("🛡️ Environment & Safety Controls")
env_choice = st.sidebar.selectbox("Trading Environment", ["PAPER", "SHADOW", "SANDBOX", "LIVE"], index=0)
st.sidebar.info(f"Active Environment: **{session.env.value}**")

kill_switch_active = session.kill_switch.is_active
if kill_switch_active:
    st.sidebar.error(f"🚨 KILL SWITCH ACTIVE: {session.kill_switch.reason}")
    if st.sidebar.button("Deactivate Kill Switch (Operator Reset)"):
        try:
            session.kill_switch.deactivate(operator_override=True)
            st.sidebar.success("Kill Switch reset successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(str(e))
else:
    st.sidebar.success("🟢 CIRCUIT BREAKER: OPERATIONAL")
    if st.sidebar.button("🚨 TRIGGER EMERGENCY STOP"):
        session.kill_switch.activate("Operator manual emergency stop triggered from dashboard UI")
        st.rerun()

# Top Metrics Row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Environment", session.env.value)
c2.metric("Execution Mode", session.broker.__class__.__name__)
c3.metric("Real Money Status", "ENABLED" if safety_status["real_money_active"] else "DISABLED", delta="Two-Key Guard Active")
c4.metric("Cash Balance", f"${session.cash:,.2f}")
c5.metric("Total Equity", f"${session.equity:,.2f}")

if safety_status["real_money_active"]:
    st.warning("⚠️ LIVE TRADING IS ENABLED. Real orders will be dispatched to connected broker!")

st.divider()

# Workstation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Market Stream & Execution", "📜 Orders, Fills & Lineage", "🔍 Reconciliation Engine", "🛡️ Hard Risk Limits"])

provider = MockMarketDataProvider()
quote = provider.get_quote("AAPL")

with tab1:
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.subheader("Live Market Data Stream (AAPL)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Last Price", f"${quote['last']:.2f}")
        m2.metric("Bid", f"${quote['bid']:.2f}")
        m3.metric("Ask", f"${quote['ask']:.2f}")

        bars_df = provider.get_bars("AAPL", limit=30)
        fig_price = px.line(bars_df, x="timestamp", y="close", markers=True, title="Intraday Bar Feed (AAPL)")
        fig_price.update_layout(template="plotly_dark")
        st.plotly_chart(fig_price, use_container_width=True)

    with col_r:
        st.subheader("Order Execution Trigger")
        st.info(f"Target Broker: **{session.broker.__class__.__name__}**")

        side = st.radio("Order Side", ["BUY", "SELL"], horizontal=True)
        qty = st.number_input("Order Quantity", min_value=1.0, max_value=1000.0, value=10.0, step=1.0)

        if st.button("🚀 Submit Order via Broker Interface"):
            bar = {"symbol": "AAPL", "close": quote["last"], "timestamp": datetime.now(timezone.utc).isoformat(), "volume": 10000}
            res = session.process_tick_or_bar("AAPL", bar)

            if res.get("status") == "PROCESSED":
                st.success(f"Processed order execution cleanly in environment '{session.env.value}'!")
                st.json(res.get("executed_orders", []))
            else:
                st.error(f"Execution Blocked: {res.get('reason', 'Rejected')}")

with tab2:
    st.subheader("Orders, Fills & Order Lineage Audit")
    col_orders, col_fills = st.columns(2)

    with col_orders:
        st.markdown("#### Broker Orders")
        orders = session.broker.get_orders()
        if orders:
            st.dataframe(pd.DataFrame(orders), use_container_width=True)
        else:
            st.info("No orders recorded for this session.")

    with col_fills:
        st.markdown("#### Broker Fills")
        fills = session.broker.get_fills()
        if fills:
            st.dataframe(pd.DataFrame(fills), use_container_width=True)
        else:
            st.info("No fills executed yet.")

    st.markdown("#### End-to-End Signal ➔ Fill Lineage Records")
    lineage_recs = session.lineage_tracker.get_all_records()
    if lineage_recs:
        st.dataframe(pd.DataFrame(lineage_recs), use_container_width=True)
    else:
        st.info("No lineage records tracked yet.")

with tab3:
    st.subheader("Position & Account Reconciliation Engine")
    st.markdown("Compares **Authoritative Broker Snapshot** against **Local Database State**")

    if st.button("🔄 Trigger Position Reconciliation Audit"):
        rec_res = session.trigger_reconciliation()
        if rec_res.is_reconciled:
            st.success(f"✅ RECONCILIATION PASSED: {rec_res.status_summary}")
        else:
            st.error(f"🚨 RECONCILIATION FAILED: {rec_res.status_summary}")
        st.json(rec_res.to_dict())

with tab4:
    st.subheader("Pre-Trade Risk Gate & Hard Limits")
    st.markdown("Hard Limits strictly **override** AI Model signals before order generation.")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Max Position Cap", "30.0% ($30,000)")
    r2.metric("Max Gross Exposure", "100.0%")
    r3.metric("Max Daily Loss Limit", "5.0% ($5,000)")
    r4.metric("Max Rate Limit", "60 Orders / Min")

    st.json({
        "hard_risk_limits": {
            "max_position_value": session.risk_gate.hard_limits_engine.config.max_position_value,
            "max_position_percent": session.risk_gate.hard_limits_engine.config.max_position_percent,
            "max_daily_loss": session.risk_gate.hard_limits_engine.config.max_daily_loss,
            "max_orders_per_minute": session.risk_gate.hard_limits_engine.config.max_orders_per_minute,
            "stale_data_gate": "ACTIVE (< 15s)"
        },
        "two_key_safety_guard": safety_status
    })
