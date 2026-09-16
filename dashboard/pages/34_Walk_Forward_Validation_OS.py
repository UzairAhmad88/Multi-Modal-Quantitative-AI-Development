"""
QUANT AI Workspace — Page 34: Walk-Forward Validation & Out-of-Sample OS Dashboard.
Provides interactive temporal fold visualizer, out-of-sample metrics, data leakage diagnostics, and test set lock control.
"""

import streamlit as st
import pandas as pd
import numpy as np

from validation.services.walk_forward_service import WalkForwardService
from validation.reports.generator import WalkForwardReportGenerator

st.set_page_config(page_title="Walk-Forward Validation OS", layout="wide")

st.title("🛡️ Walk-Forward & Out-of-Sample Validation OS")
st.caption("Temporal Cross-Validation, Purged Folds, Embargo, Data Leakage Audits & Anti-Overfitting Research Framework")

st.info("🔒 **RESEARCH ONLY & NO-LIVE-TRADING SAFETY**: All fold metrics, purging windows, and leakage audits are for quantitative model validation. Live trading remains strictly disabled.")

# Sidebar Configuration
st.sidebar.header("⚙️ Walk-Forward Configuration")
experiment_id = st.sidebar.text_input("Experiment ID", "EXP-WALKFORWARD-001")
method = st.sidebar.selectbox("Split Method", ["EXPANDING", "ROLLING", "ANCHORED", "PURGED_CV"])
train_window = st.sidebar.number_input("Train Window Size (Days)", value=250, min_value=50, step=25)
val_window = st.sidebar.number_input("Validation Window Size (Days)", value=50, min_value=10, step=10)
test_window = st.sidebar.number_input("Test Window Size (Days)", value=50, min_value=10, step=10)
purge_period = st.sidebar.number_input("Purge Horizon Steps", value=5, min_value=0, step=1)
embargo_period = st.sidebar.number_input("Embargo Window Steps", value=5, min_value=0, step=1)
lock_test_set = st.sidebar.checkbox("Lock Final Test Set (TEST_SET_LOCKED)", value=False)

service = WalkForwardService()

if st.sidebar.button("🚀 Run Walk-Forward Validation"):
    with st.spinner("Executing time-aware walk-forward validation and data leakage audits..."):
        res = service.run_walk_forward(
            experiment_id=experiment_id,
            method=method,
            train_window_size=train_window,
            val_window_size=val_window,
            test_window_size=test_window,
            purge_period=purge_period,
            embargo_period=embargo_period,
            lock_test_set=lock_test_set,
        )
        st.session_state["wf_result"] = res
        st.success(f"Walk-Forward Run Complete: {res['validation_id']}")

res = st.session_state.get("wf_result")

if not res:
    # Run a default baseline preview
    res = service.run_walk_forward(experiment_id=experiment_id, method=method)
    st.session_state["wf_result"] = res

metrics = res.get("oos_metrics", {})
leakage = res.get("leakage_audit", {})
robustness = res.get("robustness_metrics", {}).get("performance_stability", {})

# Top KPIs
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Validation ID", res.get("validation_id", "N/A"))
col2.metric("Mean OOS Sharpe", f"{metrics.get('mean_out_of_sample_sharpe', 0.0):.2f}")
col3.metric("OOS Sharpe Std", f"{metrics.get('std_out_of_sample_sharpe', 0.0):.2f}")
col4.metric("Stability Score", f"{robustness.get('stability_score', 0.0):.2f}")
col5.metric("Leakage Status", leakage.get("status", "CLEAN"))

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 OOS Performance",
    "📅 Fold Timeline",
    "🔍 Leakage Diagnostics",
    "🏋️ Robustness Analysis",
    "📄 Markdown Report",
])

with tab1:
    st.subheader("Out-of-Sample Performance Summary")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Aggregated OOS Metrics")
        st.json(metrics)

    with c2:
        st.markdown("### Fold Sharpe Ratio Distribution")
        windows = res.get("windows", [])
        sharpe_data = [
            {"Fold": w["window_id"], "OOS Sharpe": w.get("evaluation", {}).get("trading_metrics", {}).get("sharpe_ratio", 0.0)}
            for w in windows
        ]
        if sharpe_data:
            df_s = pd.DataFrame(sharpe_data)
            st.bar_chart(df_s.set_index("Fold"))

with tab2:
    st.subheader("Walk-Forward Temporal Folds")
    windows = res.get("windows", [])
    if windows:
        fold_table = []
        for w in windows:
            ev = w.get("evaluation", {}).get("trading_metrics", {})
            fold_table.append({
                "Fold ID": w.get("window_id"),
                "Train Bound": f"{w.get('train_start')} → {w.get('train_end')}",
                "Val Bound": f"{w.get('validation_start')} → {w.get('validation_end')}",
                "Test Bound": f"{w.get('test_start')} → {w.get('test_end')}",
                "Purged Steps": w.get("purged_samples"),
                "Embargo Steps": w.get("embargoed_samples"),
                "OOS Sharpe": ev.get("sharpe_ratio", 0.0),
            })
        st.dataframe(pd.DataFrame(fold_table), use_container_width=True)

with tab3:
    st.subheader("Data Leakage Diagnostic Audit")
    st.json(leakage)
    if leakage.get("issues"):
        st.warning("Detected Leakage Issues:")
        for issue in leakage["issues"]:
            st.write(f"- ⚠️ {issue}")
    else:
        st.success("✅ Zero Data Leakage Detected (Feature timestamps, availability lags, target correlation clean).")

with tab4:
    st.subheader("Performance & Parameter Stability")
    st.json(res.get("robustness_metrics", {}))

with tab5:
    st.subheader("Generated Walk-Forward Markdown Report")
    md_report = WalkForwardReportGenerator.generate_walk_forward_report(res)
    st.code(md_report, language="markdown")
