"""
Streamlit Page: Automated Quant Research Orchestrator OS.
"""

import streamlit as st
import pandas as pd
import json

from orchestrator.core.orchestrator import ResearchOrchestrator
from orchestrator.planner.research_plan import ResearchPlan
from orchestrator.planner.experiment_planner import ExperimentPlanner
from orchestrator.campaigns.campaign_manager import CampaignManager
from orchestrator.monitoring.workflow_monitor import WorkflowMonitor

st.set_page_config(page_title="Automated Research Orchestrator OS", page_icon="⚙️", layout="wide")

orchestrator = ResearchOrchestrator()
campaign_mgr = CampaignManager()

st.title("⚙️ Automated Quant Research Orchestrator OS")
st.caption("Pipeline Orchestration, Workflow DAG Execution, Validation Gates, Policy Engine & Research Campaigns")

tabs = st.tabs([
    "Workflow Builder & Launcher",
    "Live DAG & Task Progress",
    "Research Campaign Matrix",
    "Validation Gates & Policy Engine",
    "System Resources & Job Queue Monitor",
])

with tabs[0]:
    st.subheader("Build & Launch Research Workflow")
    col1, col2 = st.columns([1, 2])

    with col1:
        wf_name = st.text_input("Workflow Name", "Multimodal Quant Research Pipeline")
        template = st.selectbox("Workflow Template", ["full_research", "multimodal"])
        dataset_id = st.text_input("Dataset ID", "DS-SP500_DAILY-v1.0.0")
        model_type = st.selectbox("Model Type", ["xgboost", "lstm", "transformer", "multimodal"])
        slippage_bps = st.number_input("Slippage (bps)", value=5.0)
        fee_bps = st.number_input("Fee (bps)", value=10.0)

        if st.button("Create & Execute Workflow", type="primary"):
            custom_config = {
                "dataset_id": dataset_id,
                "model_type": model_type,
                "slippage_bps": slippage_bps,
                "fee_bps": fee_bps,
            }
            wf = orchestrator.create_workflow(name=wf_name, template=template, custom_config=custom_config)
            validated = orchestrator.validate_workflow(wf.workflow_id)
            res_wf = orchestrator.start_workflow(wf.workflow_id)

            st.session_state["active_wf_id"] = res_wf.workflow_id
            st.success(f"Workflow Executed Successfully: {res_wf.workflow_id} (Status: {res_wf.status.value})")

    with col2:
        st.subheader("Workflow Status & Outputs")
        if "active_wf_id" in st.session_state:
            wf_id = st.session_state["active_wf_id"]
            wf = orchestrator.get_workflow(wf_id)
            if wf:
                progress = WorkflowMonitor.get_progress(wf)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Workflow ID", wf.workflow_id)
                m2.metric("Status", wf.status.value)
                m3.metric("Progress", f"{progress['percent_complete']}%")
                m4.metric("Completed Tasks", f"{progress['completed_tasks']}/{progress['total_tasks']}")

                st.markdown("#### Execution Configuration")
                st.json(wf.configuration)

with tabs[1]:
    st.subheader("Live Task DAG Progress Breakdown")
    if "active_wf_id" in st.session_state:
        wf_id = st.session_state["active_wf_id"]
        wf = orchestrator.get_workflow(wf_id)
        if wf:
            tasks_data = [
                {
                    "Task ID": t.task_id,
                    "Name": t.name,
                    "Task Type": t.task_type,
                    "Depends On": ", ".join(t.depends_on) if t.depends_on else "None",
                    "Status": t.status.value,
                    "Error": t.error or "None",
                }
                for t in wf.tasks
            ]
            st.dataframe(pd.DataFrame(tasks_data), use_container_width=True)

            st.markdown("#### Real-Time Event Audit Log")
            events = orchestrator.get_events(wf_id)
            st.dataframe(pd.DataFrame(events), use_container_width=True)
    else:
        st.info("Launch a workflow to view live DAG task execution.")

with tabs[2]:
    st.subheader("Research Campaign Matrix Generator")
    col_c1, col_c2 = st.columns([1, 2])

    with col_c1:
        cmp_name = st.text_input("Campaign Name", "Multimodal Alpha Campaign")
        cmp_obj = st.text_input("Objective", "Evaluate model architecture x modality matrix")
        models_sel = st.multiselect("Models", ["xgboost", "lstm", "transformer"], default=["xgboost", "lstm"])
        modalities_sel = st.multiselect("Modalities", ["market", "market_news", "all"], default=["market", "all"])
        max_exp = st.number_input("Max Experiments Budget", value=10)

        if st.button("Generate Campaign Matrix"):
            plan = ResearchPlan(
                plan_id=f"PLAN-{cmp_name.upper()[:6]}",
                name=cmp_name,
                objective=cmp_obj,
                hypothesis="Multi-modal features improve Sharpe",
                dataset_id="DS-SP500_DAILY-v1.0.0",
                models=models_sel,
                modalities=modalities_sel,
            )
            plan.resource_budget.max_experiments = max_exp
            c = campaign_mgr.create_campaign(name=cmp_name, objective=cmp_obj, plan=plan)
            st.session_state["active_campaign_id"] = c.campaign_id
            st.success(f"Campaign Created: {c.campaign_id} ({len(c.experiments)} experiments generated)")

    with col_c2:
        if "active_campaign_id" in st.session_state:
            cid = st.session_state["active_campaign_id"]
            c = campaign_mgr.get_campaign(cid)
            if c:
                st.markdown(f"### Campaign Matrix ({len(c.experiments)} Experiments)")
                exp_table = [
                    {
                        "Experiment ID": e.experiment_id,
                        "Name": e.name,
                        "Model": e.model_version,
                        "Feature Set": e.feature_version,
                        "Dataset": e.dataset_id,
                    }
                    for e in c.experiments
                ]
                st.dataframe(pd.DataFrame(exp_table), use_container_width=True)
        else:
            st.info("Generate a research campaign to view the matrix.")

with tabs[3]:
    st.subheader("Validation Gates & Policy Engine Verification")
    if "active_wf_id" in st.session_state:
        wf_id = st.session_state["active_wf_id"]
        wf = orchestrator.get_workflow(wf_id)
        if wf:
            policies = orchestrator.policy_engine.evaluate_all(wf.configuration)
            st.dataframe(pd.DataFrame([p.dict() for p in policies]), use_container_width=True)
    else:
        st.info("Run workflow validation to view policy gate results.")

with tabs[4]:
    st.subheader("System Hardware & Job Queue Monitor")
    health = orchestrator.get_health()
    sys_res = health.get("system_resources", {})

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CPU Usage", f"{sys_res.get('cpu_percent', 0.0)}%")
    m2.metric("RAM Usage", f"{sys_res.get('memory_percent', 0.0)}%")
    m3.metric("RAM Used", f"{sys_res.get('memory_used_gb', 0.0)} GB")
    m4.metric("RAM Total", f"{sys_res.get('memory_total_gb', 0.0)} GB")

    st.markdown("#### Engine Integration Health Status")
    st.json(health.get("components", {}))
