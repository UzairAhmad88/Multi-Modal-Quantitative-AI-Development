"""
Streamlit Page: Automated Research Pipeline & Experiment Orchestration (Phase 14)
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from research.registry.registry import ExperimentRegistry
from orchestration.pipeline import ResearchPipeline
from orchestration.logging_manager import LoggingManager

st.set_page_config(page_title="Research Orchestration Pipeline", layout="wide")

st.title("⚡ Automated Research Pipeline & Experiment Orchestration")
st.markdown("Automated 17-stage end-to-end quantitative research workflow, checkpointing, and execution lineage.")

registry = ExperimentRegistry()

tabs = st.tabs(["🚀 Trigger Experiment", "📊 Pipeline Status & Graph", "🔍 Run Inspector & Artifacts", "⚖️ Compare Experiments", "📜 Live Log Viewer"])

# TAB 1: Trigger Experiment
with tabs[0]:
    st.header("Trigger New Research Experiment")
    col1, col2 = st.columns([1, 1])

    with col1:
        exp_name = st.text_input("Experiment Name", value="multimodal_baseline")
        model_type = st.selectbox("Model Type", ["multimodal", "market_only", "market_news", "lstm", "transformer"])
        seed = st.number_input("Random Seed", value=42, step=1)
        symbols = st.multiselect("Symbols", ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "TSLA"], default=["AAPL", "MSFT"])

    with col2:
        start_date = st.date_input("Start Date", value=datetime(2020, 1, 1))
        end_date = st.date_input("End Date", value=datetime(2025, 1, 1))
        initial_capital = st.number_input("Initial Capital ($)", value=100000.0, step=10000.0)
        walk_forward = st.checkbox("Walk Forward Validation", value=True)
        leakage_detection = st.checkbox("Leakage Detection", value=True)

    if st.button("🚀 Launch Research Pipeline", type="primary"):
        config = {
            "experiment": {"name": exp_name, "description": f"{model_type} quantitative research experiment", "seed": seed},
            "data": {"symbols": symbols, "start": str(start_date), "end": str(end_date)},
            "features": {"market": True, "news": True, "fundamentals": True},
            "model": {"type": model_type, "version": "1.0"},
            "backtest": {"initial_capital": initial_capital, "transaction_cost": 0.001, "slippage": 0.0005},
            "validation": {"walk_forward": walk_forward, "leakage_detection": leakage_detection, "bootstrap": True},
            "report": {"generate": True}
        }

        with st.spinner("Executing 17-Stage Research Pipeline..."):
            pipeline = ResearchPipeline(config=config)
            run_record = pipeline.execute()

        st.success(f"Pipeline Completed! Status: {run_record.get('status')} | Run ID: {run_record.get('run_id')}")
        st.json(run_record.get("metrics", {}))

# TAB 2: Pipeline Status & Graph
with tabs[1]:
    st.header("Pipeline Stages Execution Graph")
    st.markdown("""
    ```text
    [DATA] ➔ [VALIDATION] ➔ [FEATURES] ➔ [SPLIT] ➔ [MODEL TRAIN] ➔ [PREDICTION] ➔ [SIGNAL] ➔ [PORTFOLIO] ➔ [BACKTEST] ➔ [VALIDATION] ➔ [ROBUSTNESS] ➔ [STRESS] ➔ [STATS] ➔ [FINDING] ➔ [REPORT] ➔ [ARTIFACT REGISTRY]
    ```
    """)

    runs = registry.list_experiments()
    if runs:
        df_runs = pd.DataFrame([
            {
                "Run ID": r.get("run_id"),
                "Experiment ID": r.get("experiment_id"),
                "Status": r.get("status"),
                "Model": r.get("config", {}).get("model", {}).get("type"),
                "Timestamp": r.get("timestamp")
            }
            for r in runs
        ])
        st.dataframe(df_runs, use_container_width=True)
    else:
        st.info("No experiment runs recorded yet.")

# TAB 3: Run Inspector & Artifacts
with tabs[2]:
    st.header("Run Inspector & Artifact Lineage")
    runs = registry.list_experiments()
    run_ids = [r.get("run_id") for r in runs if r.get("run_id")]
    if run_ids:
        selected_run_id = st.selectbox("Select Run ID", run_ids)
        run_data = registry.get_run(selected_run_id)
        if run_data:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Run Overview")
                st.json({
                    "run_id": run_data.get("run_id"),
                    "experiment_id": run_data.get("experiment_id"),
                    "status": run_data.get("status"),
                    "timestamp": run_data.get("timestamp")
                })
                st.subheader("Metrics")
                st.json(run_data.get("metrics", {}))
            with c2:
                st.subheader("Artifact Manifest")
                st.json(run_data.get("artifacts", {}))
                st.subheader("Configuration")
                st.json(run_data.get("config", {}))
    else:
        st.info("No runs available to inspect.")

# TAB 4: Compare Experiments
with tabs[3]:
    st.header("Compare Experiments & Metrics")
    runs = registry.list_experiments()
    run_ids = [r.get("run_id") for r in runs if r.get("run_id")]
    if len(run_ids) >= 2:
        col_a, col_b = st.columns(2)
        with col_a:
            r1 = st.selectbox("Run 1", run_ids, index=0)
        with col_b:
            r2 = st.selectbox("Run 2", run_ids, index=1)

        if st.button("⚖️ Compare Runs"):
            res = registry.compare_runs(r1, r2)
            if "error" not in res:
                metrics_df = pd.DataFrame(res.get("metrics", {})).T
                st.dataframe(metrics_df, use_container_width=True)
            else:
                st.error(res["error"])
    else:
        st.info("At least two experiment runs are required for comparison.")

# TAB 5: Live Log Viewer
with tabs[4]:
    st.header("Pipeline Run Execution Logs")
    runs = registry.list_experiments()
    run_ids = [r.get("run_id") for r in runs if r.get("run_id")]
    if run_ids:
        log_run_id = st.selectbox("Select Run ID for Logs", run_ids, key="log_run_select")
        lm = LoggingManager(run_id=log_run_id)
        logs = lm.read_logs(limit=200)
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        else:
            st.info("No logs found for selected run ID.")
    else:
        st.info("No runs available.")
