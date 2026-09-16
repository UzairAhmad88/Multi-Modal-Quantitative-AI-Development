"""
Streamlit Page: Research Evaluation, Statistical Validation, Walk-Forward & Overfitting OS.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from research_evaluation.manager import ResearchEvaluationManager

st.set_page_config(page_title="Research Evaluation OS", page_icon="🔬", layout="wide")
mgr = ResearchEvaluationManager()

st.title("🔬 Research Evaluation, Statistical Validation & Overfitting OS")
st.caption("Out-of-Sample Walk-Forward Testing, Bootstrap CIs, Regime Shocks, Multimodal Ablation & Research Reports")

tabs = st.tabs(["Strategy Evaluator", "Statistical Significance & Bootstrap", "Walk-Forward & Regimes", "Ablation & Reports"])

with tabs[0]:
    st.subheader("Interactive Strategy Research Evaluator")
    col1, col2 = st.columns([1, 2])

    with col1:
        strategy_id = st.text_input("Strategy ID", "STRATEGY-20260916-0001")
        risk_free = st.number_input("Risk-Free Rate (Annual)", value=0.02)
        n_periods = st.slider("Simulation History Length (Days)", 100, 1000, 500, 50)
        seed = st.number_input("Random Seed", value=42)

        if st.button("Run Full Strategy Evaluation", type="primary"):
            np.random.seed(seed)
            rets = np.random.normal(loc=0.0008, scale=0.012, size=n_periods).tolist()
            m_rets = np.random.normal(loc=0.0004, scale=0.010, size=n_periods).tolist()

            res = mgr.evaluate_strategy(strategy_id=strategy_id, returns=rets, market_returns=m_rets)
            st.session_state["latest_eval"] = res
            st.success(f"Strategy Evaluation Complete: {res['evaluation_id']}")

    with col2:
        st.subheader("Performance Ratios & Overfitting Diagnostics")
        if "latest_eval" in st.session_state:
            res = st.session_state["latest_eval"]
            perf = res["performance"]
            overfit = res["overfitting"]

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("CAGR", f"{perf['cagr']:.2%}")
            m2.metric("Sharpe Ratio", f"{perf['sharpe_ratio']:.2f}")
            m3.metric("Sortino Ratio", f"{perf['sortino_ratio']:.2f}")
            m4.metric("Max Drawdown", f"{perf['max_drawdown']:.2%}")

            st.markdown("#### Overfitting Diagnostics")
            st.info(f"Overfitting Risk Level: **{overfit['overfitting_risk_level']}** | Deflated Sharpe: **{overfit['deflated_sharpe']:.2f}**")
            st.dataframe(pd.DataFrame([overfit]), use_container_width=True)

with tabs[1]:
    st.subheader("Statistical Significance & Bootstrap Confidence Intervals")
    if "latest_eval" in st.session_state:
        res = st.session_state["latest_eval"]
        boot = res["bootstrap"]
        sig = res["significance"]
        perm = res["permutation"]

        c1, c2, c3 = st.columns(3)
        c1.metric("Bootstrap Sharpe 95% CI", f"[{boot['ci_lower']:.2f}, {boot['ci_upper']:.2f}]")
        c2.metric("t-Statistic (p-val)", f"{sig['t_statistic']:.2f} ({sig['p_value_one_tailed']:.4f})")
        c3.metric("Permutation Test p-val", f"{perm['permutation_p_value']:.4f}")

        st.json({"bootstrap": boot, "significance": sig, "permutation": perm, "stationarity": res["stationarity"]})
    else:
        st.info("Run an evaluation to view statistical tests.")

with tabs[2]:
    st.subheader("Out-of-Sample Walk-Forward & Market Regime Breakdown")
    if "latest_eval" in st.session_state:
        res = st.session_state["latest_eval"]
        wf = res["walk_forward"]
        reg = res["regimes"]

        st.markdown(f"#### Walk-Forward Summary (OOS Sharpe: **{wf['out_of_sample_sharpe']:.2f}**)")
        st.dataframe(pd.DataFrame(wf.get("windows", [])), use_container_width=True)

        st.markdown("#### Market Regime Performance Breakdown")
        st.dataframe(pd.DataFrame(reg.get("by_regime", {})).T, use_container_width=True)
    else:
        st.info("Run an evaluation to view walk-forward and regime breakdown.")

with tabs[3]:
    st.subheader("Multimodal Ablation Study & Interactive HTML Research Report")
    if "latest_eval" in st.session_state:
        res = st.session_state["latest_eval"]
        ablation = res["ablation"]

        st.markdown("#### Modality Ablation Matrix")
        st.dataframe(pd.DataFrame(ablation["ablation_study"]).T, use_container_width=True)

        st.markdown("#### Generated Markdown Report Preview")
        st.markdown(res["markdown_report"])
    else:
        st.info("Run an evaluation to view ablation studies and research reports.")
