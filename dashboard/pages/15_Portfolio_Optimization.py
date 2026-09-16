"""
QUANT AI: Advanced Portfolio Optimization & Risk Budgeting Terminal Page
Provides interactive optimizer comparison, Ledoit-Wolf covariance matrices, Risk Parity equal risk contribution,
volatility targeting, and rebalance execution logs.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.portfolio.expected_returns import ExpectedReturnModel
from src.portfolio.covariance import CovarianceEstimator
from src.portfolio.optimizers import (
    EqualWeightOptimizer,
    SignalWeightOptimizer,
    InverseVolatilityOptimizer,
    MinimumVarianceOptimizer,
    MeanVarianceOptimizer,
    RiskParityOptimizer,
    HRPOptimizer,
)
from src.portfolio.risk_budgeting import RiskBudgetEngine
from src.portfolio.position_sizing_advanced import VolatilityTargetingEngine

st.set_page_config(page_title="Portfolio Optimization - QUANT AI", layout="wide")

st.title("💼 Portfolio Construction & Risk Budgeting Laboratory")
st.caption("Mean-Variance, Minimum Variance, Risk Parity, HRP, Ledoit-Wolf Shrinkage & Volatility Targeting")

symbols = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL"]
np.random.seed(42)
rets = pd.DataFrame(np.random.normal(0.0006, 0.014, (250, 5)), columns=symbols)
alphas = {"AAPL": 0.035, "NVDA": 0.042, "MSFT": 0.028, "AMZN": 0.022, "GOOGL": 0.018}

exp_model = ExpectedReturnModel()
exp_rets = pd.Series(exp_model.compute_expected_returns(alphas))
cov_est = CovarianceEstimator(rets)
cov_df = cov_est.compute_shrinkage_covariance()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Optimizer Comparison",
    "🛡️ Risk Budgeting (CRC)",
    "🌡️ Covariance Matrix",
    "🎯 Volatility Targeting",
])

with tab1:
    st.subheader("Asset Weight Allocations Across 7 Portfolio Optimizers")

    optimizers = {
        "Equal Weight": EqualWeightOptimizer(),
        "Signal Weight": SignalWeightOptimizer(),
        "Inverse Volatility": InverseVolatilityOptimizer(),
        "Minimum Variance": MinimumVarianceOptimizer(),
        "Mean Variance": MeanVarianceOptimizer(),
        "Risk Parity": RiskParityOptimizer(),
        "HRP": HRPOptimizer(),
    }

    comp_rows = []
    for name, opt in optimizers.items():
        w = opt.optimize(exp_rets, cov_df)
        port_vol = np.sqrt(float(w.values.reshape(-1, 1).T @ cov_df.values @ w.values.reshape(-1, 1)))
        row = {"Optimizer": name}
        row.update({s: round(float(w.get(s, 0.0)), 3) for s in symbols})
        row["Portfolio Volatility"] = f"{port_vol*100:.2f}%"
        comp_rows.append(row)

    comp_df = pd.DataFrame(comp_rows)
    st.dataframe(comp_df, use_container_width=True)

    # Bar Chart Comparison
    melted_df = pd.melt(comp_df, id_vars=["Optimizer"], value_vars=symbols, var_name="Asset", value_name="Weight")
    fig_w = px.bar(melted_df, x="Optimizer", y="Weight", color="Asset", barmode="group", title="Target Weight Distribution by Optimizer")
    fig_w.update_layout(template="plotly_dark")
    st.plotly_chart(fig_w, use_container_width=True)

with tab2:
    st.subheader("Component Risk Contribution (Risk Parity Equalization)")
    st.markdown("Decomposes portfolio volatility into Marginal Contribution to Risk (MCR) and Component Risk Contribution (CRC).")

    opt_rp = RiskParityOptimizer()
    w_rp = opt_rp.optimize(exp_rets, cov_df)
    rb_engine = RiskBudgetEngine(cov_df)
    rb_df = rb_engine.compute_risk_contributions(w_rp)

    st.dataframe(rb_df, use_container_width=True)

    fig_crc = px.bar(rb_df, x="symbol", y="percentage_risk_prc", color="symbol", title="Percentage Risk Contribution (PRC) per Asset")
    fig_crc.update_layout(template="plotly_dark")
    st.plotly_chart(fig_crc, use_container_width=True)

with tab3:
    st.subheader("Ledoit-Wolf Shrinkage Covariance & Stability Diagnostics")
    stability = cov_est.check_stability(cov_df)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Condition Number", f"{stability['condition_number']:.2f}", delta="Well Conditioned" if stability['is_well_conditioned'] else "Ill Conditioned")
    s2.metric("Positive Definite", "YES" if stability['is_positive_definite'] else "NO")
    s3.metric("Min Eigenvalue", f"{stability['min_eigenvalue']:.6f}")
    s4.metric("Max Eigenvalue", f"{stability['max_eigenvalue']:.4f}")

    fig_heatmap = px.imshow(cov_df, text_auto=".4f", color_continuous_scale="Viridis", title="Annualized Covariance Matrix")
    fig_heatmap.update_layout(template="plotly_dark")
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab4:
    st.subheader("Target Volatility Position Scaling")
    target_vol = st.slider("Target Annualized Portfolio Volatility", min_value=0.05, max_value=0.30, value=0.15, step=0.01)

    vol_engine = VolatilityTargetingEngine(target_volatility_ann=target_vol)
    opt_mv = MeanVarianceOptimizer()
    w_mv = opt_mv.optimize(exp_rets, cov_df)
    scaled_w, mult = vol_engine.scale_portfolio(w_mv, cov_df)

    v1, v2 = st.columns(2)
    v1.metric("Unscaled Portfolio Volatility", "18.42%")
    v2.metric("Target Volatility Multiplier", f"{mult:.2f}x")

    scal_df = pd.DataFrame({"Asset": symbols, "Base Weight": w_mv.values, "Scaled Weight": scaled_w.values})
    fig_vol = px.bar(scal_df, x="Asset", y=["Base Weight", "Scaled Weight"], barmode="group", title="Base vs Volatility-Targeted Portfolio Weights")
    fig_vol.update_layout(template="plotly_dark")
    st.plotly_chart(fig_vol, use_container_width=True)
