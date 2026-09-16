"""
Streamlit Workstation Dashboard Page 32: Portfolio Construction & Optimization Engine OS.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from portfolio.services.portfolio_service import PortfolioService
from portfolio.reports.generator import PortfolioReportGenerator
from portfolio.risk.attribution import PortfolioRiskAttribution
from portfolio.constraints.engine import ConstraintEngine

st.set_page_config(page_title="Portfolio Construction OS", page_icon="💼", layout="wide")

st.title("💼 Portfolio Construction & Optimization Engine OS")
st.caption("Phase 25 Institutional Portfolio Construction, Position Sizing, Risk Attribution, Constraints & Turnover Control")

service = PortfolioService()

# Sidebar Control Panel
st.sidebar.header("⚙️ Portfolio Configuration")
portfolio_id = st.sidebar.text_input("Portfolio ID", value="PORT-DEMO-001")
optimizer_method = st.sidebar.selectbox(
    "Optimization Method",
    options=["mean_variance", "risk_parity", "min_variance", "equal_weight", "signal_weighted", "max_diversification", "constrained"],
    index=0,
)
risk_aversion = st.sidebar.slider("Risk Aversion (Lambda)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
max_pos_weight = st.sidebar.slider("Max Position Weight", min_value=0.05, max_value=0.50, value=0.20, step=0.05)
max_turnover = st.sidebar.slider("Max Turnover", min_value=0.10, max_value=1.00, value=0.50, step=0.05)

# Initialize Demo Portfolio
assets = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "UNH"]
alpha_scores = {
    "AAPL": 0.045, "MSFT": 0.038, "GOOGL": 0.025, "AMZN": 0.052, "NVDA": 0.085,
    "META": 0.041, "TSLA": 0.012, "JPM": 0.018, "V": 0.029, "UNH": 0.022
}

constraints_override = {
    "max_position_weight": max_pos_weight,
    "max_turnover": max_turnover,
    "risk_aversion": risk_aversion,
}

if st.sidebar.button("🚀 Run Portfolio Optimization"):
    with st.spinner("Optimizing portfolio allocations..."):
        opt_res = service.optimize_portfolio(
            portfolio_id=portfolio_id,
            method=optimizer_method,
            alpha_scores=alpha_scores,
            constraints_override=constraints_override,
        )
        st.session_state["opt_res"] = opt_res

if "opt_res" not in st.session_state:
    st.session_state["opt_res"] = service.optimize_portfolio(
        portfolio_id=portfolio_id,
        method=optimizer_method,
        alpha_scores=alpha_scores,
        constraints_override=constraints_override,
    )

opt_res = st.session_state["opt_res"]

# Layout Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Portfolio Weights",
    "🛡️ Risk Attribution",
    "🔄 Rebalance & Costs",
    "📋 Constraint Monitor",
    "📄 Validation Report",
])

with tab1:
    st.subheader("Target Portfolio Weights & Allocations")

    weights = opt_res.get("target_weights", {})
    df_weights = pd.DataFrame([
        {"Asset": a, "Target Weight (%)": w * 100.0, "Alpha Score": alpha_scores.get(a, 0.0)}
        for a, w in weights.items()
    ])

    col1, col2 = st.columns([3, 2])
    with col1:
        fig_bar = px.bar(
            df_weights,
            x="Asset",
            y="Target Weight (%)",
            color="Target Weight (%)",
            title=f"Allocations ({optimizer_method.upper()})",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.dataframe(df_weights.style.highlight_max(axis=0, subset=["Target Weight (%)"]), height=380, use_container_width=True)

with tab2:
    st.subheader("Portfolio Risk Attribution & Concentration")
    risk_attr = opt_res.get("risk_attribution", {})
    conc = risk_attr.get("concentration_metrics", {})

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Portfolio Volatility", f"{risk_attr.get('portfolio_volatility', 0.0)*100.0:.2f}%")
    m2.metric("Diversification Ratio", f"{risk_attr.get('diversification_ratio', 1.0):.4f}")
    m3.metric("Herfindahl Index (HHI)", f"{conc.get('hhi', 0.0):.4f}")
    m4.metric("Effective Assets (N_eff)", f"{conc.get('effective_n', 0.0):.2f}")

    pcr = risk_attr.get("asset_risk_contributions", {})
    df_pcr = pd.DataFrame([{"Asset": a, "Risk Contribution (%)": p * 100.0} for a, p in pcr.items()])
    fig_pie = px.pie(df_pcr, values="Risk Contribution (%)", names="Asset", title="Percentage Contribution to Risk (PCR)")
    st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.subheader("Rebalancing Preview & Cost Impact")
    cost = opt_res.get("transaction_costs", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("Estimated Cost ($)", f"${cost.get('total_cost', 0.0):,.2f}")
    c2.metric("Cost Basis Points", f"{cost.get('cost_bps', 0.0):.1f} bps")
    c3.metric("Total Traded Value", f"${cost.get('total_traded_value', 0.0):,.2f}")

    st.write("**Rebalance Event Log**")
    rebal = service.rebalance_portfolio(portfolio_id=portfolio_id, target_weights=weights)
    st.json(rebal.to_dict())

with tab4:
    st.subheader("Constraint Compliance Monitor")
    constraints = opt_res.get("constraint_status", {})
    status = constraints.get("status", "PASSED")

    if status == "PASSED":
        st.success("✅ All portfolio constraints satisfied!")
    else:
        st.error(f"❌ Constraint Infeasibility Detected: {status}")

    details = constraints.get("details", {})
    df_cons = pd.DataFrame([
        {"Constraint": name, "Passed": d["passed"], "Diagnostic Message": d["message"]}
        for name, d in details.items()
    ])
    st.dataframe(df_cons, use_container_width=True)

with tab5:
    st.subheader("Human-Readable Portfolio Construction Report")
    report_md = PortfolioReportGenerator.generate_report_md(opt_res)
    st.markdown(report_md)
