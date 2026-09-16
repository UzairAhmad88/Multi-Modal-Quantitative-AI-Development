"""
QUANT AI Workspace — Page 36: End-to-End Research Pipeline OS Dashboard.
Provides interactive 14-stage pipeline stepper, execution status logs, backtest & risk metrics, and report exporter.
"""

import streamlit as st
import pandas as pd
import numpy as np

from orchestration.services.orchestration_service import OrchestrationService
from orchestration.reports.generator import ResearchReportGenerator
from orchestration.pipeline_context import PipelineContext

st.set_page_config(page_title="Research Pipeline OS", layout="wide")

st.title("🔄 End-to-End Research Pipeline & Workflow OS")
st.caption("Unified 14-Stage Quantitative Research Pipeline: Data → Features → Validation → Training → Prediction → Alpha → Portfolio → Execution → Backtest → Risk → Statistics → Robustness → Monitoring → Report")

st.info("🔒 **RESEARCH & SIMULATION SAFETY**: All pipeline steps, portfolio weights, execution simulations, and risk stress tests are strictly for quantitative research. Live trading remains disabled.")

# Sidebar Configuration
st.sidebar.header("⚙️ Pipeline Configuration")
experiment_id = st.sidebar.text_input("Experiment ID", "EXP-PIPELINE-001")
profile = st.sidebar.selectbox("Configuration Profile", ["development.yaml", "research.yaml"])
symbols_str = st.sidebar.text_input("Universe Symbols", "AAPL, MSFT, NVDA")
symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
strict_leakage = st.sidebar.checkbox("Strict Data Leakage Gate", value=True)

service = OrchestrationService()

if st.sidebar.button("🚀 Execute Full 14-Stage Pipeline"):
    with st.spinner("Executing 14-stage quantitative research pipeline..."):
        run_state = service.run_pipeline(
            experiment_id=experiment_id,
            symbols=symbols,
            config={"strict_leakage": strict_leakage},
        )
        st.session_state["pipe_state"] = run_state
        st.success(f"Pipeline Run Complete: {run_state.run_id} ({run_state.status})")

run_state = st.session_state.get("pipe_state")

if not run_state:
    run_state = service.run_pipeline(experiment_id=experiment_id, symbols=symbols)
    st.session_state["pipe_state"] = run_state

# Top Status KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Run ID", run_state.run_id)
col2.metric("Pipeline Status", run_state.status)
col3.metric("Completed Stages", f"{len(run_state.completed_stages)} / 14")
col4.metric("Total Duration", f"{run_state.duration_seconds:.2f}s")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🚦 14-Stage Stepper & Logs", "🔗 End-to-End Lineage", "📄 Research Report"])

with tab1:
    st.subheader("14-Stage DAG Stepper")
    stage_list = [
        "DATA", "FEATURES", "VALIDATION", "TRAINING", "PREDICTION",
        "ALPHA", "PORTFOLIO", "EXECUTION", "BACKTEST", "RISK",
        "STATISTICS", "ROBUSTNESS", "MONITORING", "REPORT"
    ]

    cols = st.columns(7)
    for idx, stage in enumerate(stage_list[:7]):
        is_done = stage in run_state.completed_stages
        cols[idx].metric(stage, "✓ COMPLETED" if is_done else "PENDING")

    cols2 = st.columns(7)
    for idx, stage in enumerate(stage_list[7:]):
        is_done = stage in run_state.completed_stages
        cols2[idx].metric(stage, "✓ COMPLETED" if is_done else "PENDING")

    st.write("#### Stage Execution Logs & Timing")
    if run_state.stages:
        log_data = []
        for s_name, s_state in run_state.stages.items():
            log_data.append({
                "Stage": s_name,
                "Status": s_state.status,
                "Duration (s)": s_state.duration_seconds,
                "Error": s_state.error_message or "None",
            })
        st.dataframe(pd.DataFrame(log_data), use_container_width=True)

with tab2:
    st.subheader("Data-to-Report Lineage Tree")
    st.code(
        f"""
        DATA (DATA-v1.0)
          ↓
        FEATURES (FEAT-v1.0)
          ↓
        MODEL (MODEL-{run_state.experiment_id})
          ↓
        PREDICTIONS (PRED-{run_state.run_id[:8]})
          ↓
        ALPHA (ALPHA-{run_state.run_id[:8]})
          ↓
        PORTFOLIO (PORT-{run_state.run_id[:8]})
          ↓
        BACKTEST (BACK-{run_state.run_id[:8]})
          ↓
        RISK (RISK-{run_state.run_id[:8]})
          ↓
        MONITORING (MON-{run_state.run_id[:8]})
          ↓
        REPORT (REP-{run_state.run_id[:8]})
        """,
        language="text",
    )

with tab3:
    st.subheader("Automated Research Report Generator")
    context = PipelineContext(experiment_id=run_state.experiment_id, run_id=run_state.run_id)
    generator = ResearchReportGenerator()
    report_md = generator.generate_research_report(context)
    st.text_area("Markdown Research Report", report_md, height=450)
    st.download_button("📥 Download research_report.md", report_md, file_name=f"{run_state.run_id}_research_report.md")
