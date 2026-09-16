"""
Streamlit Page: Portfolio Optimization, Position Sizing & Risk-Aware Construction OS.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from portfolio_optimization.manager import PortfolioOptimizationManager

st.set_page_config(page_title="Portfolio Optimization OS", page_icon="⚖️", layout="wide")
mgr = PortfolioOptimizationManager()

st.title("⚖️ Portfolio Optimization, Position Sizing & Construction OS")
st.caption("Risk-Aware Optimization, Position Bounds, Transaction Costs & MCR Risk Attribution")

tabs = st.tabs(["Optimization Configurator", "Weights & Risk Attribution", "Rebalancing & Costs", "Scenario Stress Shocks"])

with tabs[0]:
    st.subheader("Interactive Portfolio Optimizer")
    col1, col2 = st.columns([1, 2])

    with col1:
        method = st.selectbox("Optimization Method", [
            "mean_variance", "risk_parity", "equal_weight", "inverse_volatility", "minimum_variance", "target_volatility"
        ])
        risk_aversion = st.slider("Risk Aversion Coefficient (γ)", 0.5, 10.0, 2.0, 0.5)
        max_weight = st.slider("Max Asset Weight Bound", 0.10, 1.00, 0.35, 0.05)
        long_only = st.checkbox("Long-Only Constraint", value=True)
        comm_bps = st.number_input("Commission (bps)", value=1.0)
        slip_bps = st.number_input("Slippage (bps)", value=5.0)

        if st.button("Run Portfolio Optimization"):
            signals = {"AAPL": 0.75, "MSFT": 0.60, "NVDA": 0.85, "AMZN": 0.50, "GOOGL": 0.40}
            config = {
                "portfolio": {"method": method, "name": f"{method}_portfolio"},
                "objective": {"risk_aversion": risk_aversion},
                "constraints": {"long_only": long_only, "max_weight": max_weight},
                "transaction_costs": {"commission_bps": comm_bps, "slippage_bps": slip_bps}
            }
            res = mgr.optimize_portfolio(alpha_signals=signals, config=config)
            st.session_state["latest_opt"] = res
            st.success(f"Optimization {res['status']}: {res['portfolio_id']}")

    with col2:
        st.subheader("Optimization Results")
        if "latest_opt" in st.session_state:
            res = st.session_state["latest_opt"]
            entry = res["entry"]
            m1, m2, m3 = st.columns(3)
            m1.metric("Status", res["status"])
            m2.metric("Expected Volatility", f"{entry['expected_volatility']:.2%}")
            m3.metric("Estimated Turnover", f"{entry['transaction_costs']['turnover']:.2%}")

            st.markdown("#### Target Allocation Weights")
            df_w = pd.DataFrame(list(entry["weights"].items()), columns=["Asset", "Target Weight"])
            st.dataframe(df_w, use_container_width=True)

with tabs[1]:
    st.subheader("Risk Contribution & Marginal Contribution to Risk (MCR)")
    if "latest_opt" in st.session_state:
        res = st.session_state["latest_opt"]
        attr = res["entry"]["risk_attribution"]
        st.dataframe(pd.DataFrame.from_dict(attr, orient="index"), use_container_width=True)
    else:
        st.info("Run an optimization in Tab 1 first.")

with tabs[2]:
    st.subheader("Rebalancing Trade Generation & Transaction Cost Breakdown")
    if "latest_opt" in st.session_state:
        res = st.session_state["latest_opt"]
        costs = res["entry"]["transaction_costs"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Trade Volume", f"${costs['total_trade_volume']:,.2f}")
        c2.metric("Commission Cost", f"${costs['commission_cost']:.2f}")
        c3.metric("Slippage Cost", f"${costs['slippage_cost']:.2f}")

        st.markdown("#### Trade Details")
        st.dataframe(pd.DataFrame.from_dict(costs["asset_trades"], orient="index"), use_container_width=True)
    else:
        st.info("Run an optimization in Tab 1 first.")

with tabs[3]:
    st.subheader("Scenario Stress Shocks")
    if "latest_opt" in st.session_state:
        res = st.session_state["latest_opt"]
        weights = res["entry"]["weights"]
        from portfolio_optimization.scenarios.scenario_engine import ScenarioEngine
        shock_mkt = ScenarioEngine.evaluate_market_shock(weights, shock_pct=-0.15)
        st.json(shock_mkt)
    else:
        st.info("Run an optimization in Tab 1 first.")
