"""
Streamlit Workstation Dashboard Page 33: Advanced Quantitative Risk & Stress Testing OS.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from risk.services.risk_service import RiskService
from risk.reports.generator import RiskReportGenerator

st.set_page_config(page_title="Advanced Risk OS", page_icon="⚡", layout="wide")

st.title("⚡ Advanced Quantitative Risk & Stress Testing Engine OS")
st.caption("Phase 26 Market Risk, Tail Risk (VaR/CVaR), Stress Testing, Monte Carlo Simulations & Limit Breach Alerts")

service = RiskService()

# Sidebar Controls
st.sidebar.header("⚙️ Risk Evaluation Setup")
portfolio_id = st.sidebar.text_input("Portfolio ID", value="PORT-DEMO-001")
mc_simulations = st.sidebar.select_slider("Monte Carlo Paths", options=[1000, 5000, 10000, 25000], value=10000)
var_confidence = st.sidebar.selectbox("VaR Confidence Level", options=[0.95, 0.99], index=0)
random_seed = st.sidebar.number_input("Stochastic Seed", value=42, step=1)

if st.sidebar.button("🚀 Run Risk Analysis"):
    with st.spinner("Executing Risk Engine & Stress Scenarios..."):
        risk_res = service.run_risk_analysis(portfolio_id=portfolio_id)
        st.session_state["risk_res"] = risk_res

if "risk_res" not in st.session_state:
    st.session_state["risk_res"] = service.run_risk_analysis(portfolio_id=portfolio_id)

risk_res = st.session_state["risk_res"]

mkt = risk_res.get("market_risk", {})
tail = risk_res.get("tail_risk", {})
dd = risk_res.get("drawdown_analysis", {})
mc = risk_res.get("monte_carlo_results", {})
limits = risk_res.get("risk_limits_status", {})
stress = risk_res.get("stress_results", {}).get("stress_results", {})

# Top KPIs
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Annual Volatility", f"{mkt.get('historical_volatility', 0.0)*100.0:.2f}%")
m2.metric("Portfolio Beta", f"{mkt.get('beta', 1.0):.2f}")
m3.metric("VaR (95% 1D)", f"{tail.get('var_95_historical', 0.0)*100.0:.2f}%")
m4.metric("CVaR (95% 1D)", f"{tail.get('cvar_95', 0.0)*100.0:.2f}%")
m5.metric("Max Drawdown", f"{dd.get('max_drawdown', 0.0)*100.0:.2f}%")
m6.metric("Limit Status", limits.get("status", "NORMAL"))

# Tabs Layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Market & Correlation",
    "🎯 Tail Risk & Drawdown",
    "💥 Stress Scenarios",
    "🎲 Monte Carlo Simulation",
    "📑 Risk Report",
])

with tab1:
    st.subheader("Asset Correlation & Factor Risk Exposure")
    corr_matrix = mkt.get("correlation", {}).get("correlation_matrix", [[1.0, 0.5], [0.5, 1.0]])
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Asset Cross-Correlation Matrix",
        zmin=-1.0, zmax=1.0,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with tab2:
    st.subheader("Historical Drawdown Series & Event Recovery")
    cum_series = dd.get("cumulative_series", [100000.0, 102000.0, 98000.0])
    dd_series = dd.get("drawdown_series", [0.0, 0.0, -0.039])

    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(y=dd_series, fill="tozeroy", name="Drawdown %", line=dict(color="red")))
    fig_dd.update_layout(title="Historical Portfolio Drawdown Depth", yaxis_tickformat=".2%")
    st.plotly_chart(fig_dd, use_container_width=True)

with tab3:
    st.subheader("Stress Test Scenario Impact Matrix")
    df_stress = pd.DataFrame([
        {
            "Scenario": s_id,
            "Stressed Value ($)": s_res.get("stressed_value", 0.0),
            "Loss ($)": s_res.get("absolute_loss", 0.0),
            "Loss (%)": s_res.get("percentage_loss", 0.0) * 100.0,
        }
        for s_id, s_res in stress.items()
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        fig_bar = px.bar(
            df_stress,
            x="Scenario",
            y="Loss (%)",
            color="Loss (%)",
            title="Stress Test Loss (%) by Scenario",
            color_continuous_scale="Reds",
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.dataframe(df_stress, height=350, use_container_width=True)

with tab4:
    st.subheader("Monte Carlo Correlated P&L Simulation")
    st.write(f"Executed **{mc.get('simulations', 10000):,}** simulation paths with seed `{mc.get('random_seed', 42)}`.")

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Monte Carlo VaR (95%)", f"${mc.get('mc_var_95', 0.0):,.2f}")
    mc2.metric("Monte Carlo CVaR (95%)", f"${mc.get('mc_cvar_95', 0.0):,.2f}")
    mc3.metric("Expected Mean P&L", f"${mc.get('mean_pnl', 0.0):,.2f}")

    # Generate synthetic P&L distribution histogram for UI display
    np.random.seed(int(mc.get("random_seed", 42)))
    pnl_samples = np.random.normal(loc=mc.get("mean_pnl", 0.0), scale=abs(mc.get("mc_var_95", 1000.0)), size=2000)
    fig_hist = px.histogram(pnl_samples, nbins=50, title="Simulated P&L Distribution ($)", labels={"value": "P&L ($)"})
    st.plotly_chart(fig_hist, use_container_width=True)

with tab5:
    st.subheader("Human-Readable Risk & Stress Report")
    report_md = RiskReportGenerator.generate_report_md(risk_res)
    st.markdown(report_md)
