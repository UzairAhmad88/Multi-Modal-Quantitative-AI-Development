"""
Streamlit Dashboard: 20_Research_Validation.py
Phase 13: Research-Grade Validation, Leakage Detection, Walk-Forward, Bootstrap CIs & Stress Testing.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validation.orchestrator import ValidationPipeline

st.set_page_config(
    page_title="Research Validation | Quant AI",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("# 🛡️ Research-Grade Validation & Robustness Lab")
st.markdown("Audit model performance for look-ahead bias, temporal walk-forward stability, statistical significance, bootstrap confidence intervals, and transaction cost stress.")

if "validation_pipeline" not in st.session_state:
    st.session_state.validation_pipeline = ValidationPipeline()

vpipe: ValidationPipeline = st.session_state.validation_pipeline

# Experiment selector
exp_id = st.text_input("Target Experiment ID for Validation Audit", "EXP-2026-000001")

if st.button("Run Full 12-Axis Validation Suite"):
    suite = vpipe.run_full_validation_suite(exp_id)
    summary = suite["validation_summary"]

    # Critical Alert Banner
    if summary["status"] == "FAILED":
        st.error("🚨 CRITICAL LEAKAGE OR QUALITY FAILURE: Validation Status = FAILED! Result must NOT be promoted as a valid finding.")
    else:
        st.success("✅ VALIDATION PASSED: No critical look-ahead leakage or price violations detected.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Validation ID", summary["validation_id"])
    with col2:
        st.metric("Walk-Forward OOS Sharpe", f"{summary['walk_forward_sharpe']:.2f}")
    with col3:
        st.metric("95% Sharpe CI", f"[{summary['sharpe_ci_low']:.2f}, {summary['sharpe_ci_high']:.2f}]")
    with col4:
        st.metric("Gen Gap (Train-Test)", f"{summary['gen_gap']:.2f}")

    st.divider()

    tabs = st.tabs([
        "📊 Validation Matrix",
        "🚨 Leakage & Timing Audit",
        "📈 Walk-Forward OOS",
        "📐 Statistical Tests & Bootstrap",
        "💥 Stress Testing & Costs",
        "🧬 Overfitting & Decay",
        "🔐 Reproducibility Hash",
    ])

    # Tab 1: Validation Matrix
    with tabs[0]:
        st.subheader("Validation Dimension Status Matrix")
        matrix_data = [
            {"Dimension": "Data Quality & Price Sanity", "Status": summary["quality_status"], "Details": f"{summary['quality_violations']} Price Violations"},
            {"Dimension": "Look-Ahead & Timing Leakage", "Status": summary["leakage_status"], "Details": summary["leakage_alert"]},
            {"Dimension": "Temporal Sequence Split", "Status": summary["temporal_status"], "Details": "Sequential Split (Purged & Embargoed)"},
            {"Dimension": "Walk-Forward CV", "Status": summary["walk_forward_status"], "Details": f"OOS Sharpe = {summary['walk_forward_sharpe']:.2f}"},
            {"Dimension": "Statistical Significance", "Status": summary["statistical_status"], "Details": f"T-Test p-value = {summary['p_value']:.4f}"},
            {"Dimension": "Bootstrap Confidence CIs", "Status": summary["bootstrap_status"], "Details": f"Sharpe 95% CI: [{summary['sharpe_ci_low']:.2f}, {summary['sharpe_ci_high']:.2f}]"},
            {"Dimension": "Transaction Cost Stress", "Status": summary["cost_stress_status"], "Details": "Survives 10 bps Cost Sweep"},
            {"Dimension": "Overfitting Diagnostics", "Status": summary["overfitting_status"], "Details": f"Generalization Gap = {summary['gen_gap']:.2f}"},
            {"Dimension": "Reproducibility Hash", "Status": summary["reproducibility_status"], "Details": f"Hash: {summary['validation_hash'][:16]}..."},
        ]
        st.dataframe(pd.DataFrame(matrix_data), use_container_width=True)

    # Tab 2: Leakage Audit
    with tabs[1]:
        st.subheader("Timestamp & Preprocessing Leakage Audit")
        st.json(suite["leakage_detection"])

    # Tab 3: Walk-Forward CV
    with tabs[2]:
        st.subheader("Walk-Forward Out-of-Sample Folds")
        wf = suite["walk_forward"]
        st.write(f"**Mode:** {wf['mode']} | **Total Folds:** {wf['total_folds']} | **Avg OOS Sharpe:** {wf['average_out_of_sample_sharpe']:.2f}")
        st.dataframe(pd.DataFrame(wf["folds"]), use_container_width=True)

    # Tab 4: Statistical Tests & Bootstrap
    with tabs[3]:
        st.subheader("Statistical Tests & 1000-Iteration Bootstrap Resampling")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Mean Return T-Test")
            st.json(suite["statistical_tests"])
        with c2:
            st.markdown("#### Bootstrap 95% Confidence Intervals")
            st.json(suite["bootstrap"])

    # Tab 5: Stress Testing
    with tabs[4]:
        st.subheader("Transaction Cost & Market Regime Stress")
        st.json(suite["stress_testing"])

    # Tab 6: Overfitting & Decay
    with tabs[5]:
        st.subheader("Generalization Gap & Performance Decay")
        st.json(suite["overfitting"])

    # Tab 7: Reproducibility Hash
    with tabs[6]:
        st.subheader("Validation Hash & Environment Snapshot")
        st.json(suite["reproducibility"])
        st.success(f"Markdown Audit Report saved at: `{suite['report_path']}`")
