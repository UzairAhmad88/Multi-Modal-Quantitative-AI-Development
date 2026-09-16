"""
Streamlit Page: Execution Simulation, Order Management & Market Microstructure OS.
"""

import streamlit as st
import pandas as pd
import json
from execution.manager import ExecutionManager

st.set_page_config(page_title="Execution Simulation OS", page_icon="⚡", layout="wide")
mgr = ExecutionManager()

st.title("⚡ Execution Simulation, Order Management & Market Microstructure OS")
st.caption("Research-Grade Order Execution Engine, Slippage, Latency, Liquidity Caps & Microstructure Analytics")

tabs = st.tabs(["Execution Simulator", "Orders & Fills Ledger", "Implementation Shortfall & Costs", "Algorithm Benchmark Comparison"])

with tabs[0]:
    st.subheader("Interactive Execution Engine")
    col1, col2 = st.columns([1, 2])

    with col1:
        portfolio_id = st.text_input("Target Portfolio ID", "PORTFOLIO-20260916-0001")
        algorithm = st.selectbox("Execution Algorithm", ["MARKET", "TWAP", "VWAP", "POV"])
        scenario = st.selectbox("Market Scenario", ["normal", "low_liquidity", "high_volatility", "delayed_execution"])

        st.markdown("#### Portfolio Rebalance Weights")
        curr_w_json = st.text_area("Current Weights JSON", '{"AAPL": 0.20, "MSFT": 0.20, "NVDA": 0.10}')
        targ_w_json = st.text_area("Target Weights JSON", '{"AAPL": 0.35, "MSFT": 0.05, "NVDA": 0.25, "GOOGL": 0.15}')

        if st.button("Run Execution Simulation", type="primary"):
            try:
                curr_w = json.loads(curr_w_json)
                targ_w = json.loads(targ_w_json)
                snaps = {
                    "AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015},
                    "MSFT": {"close": 420.0, "volume": 300000.0, "adv": 800000.0, "volatility": 0.012},
                    "NVDA": {"close": 130.0, "volume": 800000.0, "adv": 1500000.0, "volatility": 0.025},
                    "GOOGL": {"close": 175.0, "volume": 400000.0, "adv": 900000.0, "volatility": 0.018}
                }
                res = mgr.run_execution(
                    current_weights=curr_w,
                    target_weights=targ_w,
                    market_snapshots=snaps,
                    portfolio_id=portfolio_id,
                    algorithm=algorithm,
                    scenario_name=scenario
                )
                st.session_state["latest_exec"] = res
                st.success(f"Execution Simulation Complete: {res['execution_id']}")
            except Exception as e:
                st.error(f"Execution simulation failed: {e}")

    with col2:
        st.subheader("Execution Summary Metrics")
        if "latest_exec" in st.session_state:
            res = st.session_state["latest_exec"]
            summ = res["summary_report"]["summary"]

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Execution ID", res["execution_id"])
            m2.metric("Fill Rate", f"{summ['fill_rate']:.1%}")
            m3.metric("Shortfall (bps)", f"{summ['total_shortfall_bps']:.2f} bps")
            m4.metric("Mean Latency", f"{summ['mean_latency_ms']:.1f} ms")

            st.markdown("#### Generated Trades Breakdown")
            df_trades = pd.DataFrame(res["trades"])
            st.dataframe(df_trades, use_container_width=True)

with tabs[1]:
    st.subheader("Order Management System & Fills Audit Trail")
    if "latest_exec" in st.session_state:
        res = st.session_state["latest_exec"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Orders Queue")
            st.dataframe(pd.DataFrame(res["orders"]), use_container_width=True)
        with c2:
            st.markdown("#### Execution Fills Ledger")
            st.dataframe(pd.DataFrame(res["fills"]), use_container_width=True)
    else:
        st.info("Run an execution simulation to view orders and fills.")

with tabs[2]:
    st.subheader("Implementation Shortfall & Execution Cost Attribution")
    if "latest_exec" in st.session_state:
        res = st.session_state["latest_exec"]
        costs = res["cost_attribution"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Execution Cost", f"${costs['total_execution_cost']:,.2f}")
        c2.metric("Broker & Exchange Fees", f"${costs['fees']:,.2f}")
        c3.metric("Directional Slippage", f"${costs['total_slippage']:,.2f}")
        c4.metric("Total Cost (bps)", f"{costs['cost_bps']:.2f} bps")

        st.json(costs)
    else:
        st.info("Run an execution simulation to view cost breakdown.")

with tabs[3]:
    st.subheader("Execution Algorithm Comparison (MARKET vs TWAP vs VWAP vs POV)")
    if st.button("Run Multi-Algorithm Benchmark"):
        curr_w = {"AAPL": 0.1, "MSFT": 0.2}
        targ_w = {"AAPL": 0.25, "MSFT": 0.05}
        snaps = {
            "AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015},
            "MSFT": {"close": 420.0, "volume": 300000.0, "adv": 800000.0, "volatility": 0.012}
        }
        comp = {}
        for algo in ["MARKET", "TWAP", "VWAP", "POV"]:
            r = mgr.run_execution(current_weights=curr_w, target_weights=targ_w, market_snapshots=snaps, algorithm=algo)
            comp[algo] = {
                "Child Orders": r["child_orders_count"],
                "Fills": r["fills_count"],
                "Fill Rate": f"{r['summary_report']['summary']['fill_rate']:.1%}",
                "Shortfall (bps)": round(r["summary_report"]["summary"]["total_shortfall_bps"], 2),
                "Total Cost ($)": r["cost_attribution"]["total_execution_cost"]
            }
        st.dataframe(pd.DataFrame(comp).T, use_container_width=True)
