"""
Streamlit Page: Research Laboratory OS, Experiment Tracking, Knowledge Base & Reproducibility.
"""

import streamlit as st
import pandas as pd
import json
from research_lab.manager import ExperimentManager

st.set_page_config(page_title="Research Laboratory OS", page_icon="🧪", layout="wide")
mgr = ExperimentManager()

st.title("🧪 Quantitative Research Laboratory OS")
st.caption("Experiment Lifecycle Tracking, Immutable Config Hashes, Lineage DAGs, Knowledge Base & Replication")

tabs = st.tabs(["Experiment Creator", "Runs & Metrics Tracking", "Lineage DAG Visualizer", "Knowledge Base & Findings", "Replication & Reproducibility"])

with tabs[0]:
    st.subheader("Create New Research Experiment")
    col1, col2 = st.columns([1, 2])

    with col1:
        exp_name = st.text_input("Experiment Name", "Multimodal Fusion Alpha Experiment")
        template = st.selectbox("Experiment Template", ["multimodal", "prediction", "classification", "portfolio", "execution", "regime", "ablation"])
        seed = st.number_input("Random Seed", value=42)

        st.markdown("#### Hypothesis Setup")
        q = st.text_input("Research Question", "Does news sentiment improve prediction?")
        hyp = st.text_input("Hypothesis", "Fusing FinBERT news with technicals increases Sharpe ratio.")
        null_h = st.text_input("Null Hypothesis", "No significant Sharpe improvement.")

        if st.button("Create & Execute Experiment", type="primary"):
            hypothesis_dict = {
                "research_question": q,
                "hypothesis": hyp,
                "null_hypothesis": null_h,
                "success_criteria": "Sharpe >= 1.25"
            }
            exp = mgr.create_experiment(name=exp_name, template_name=template, hypothesis=hypothesis_dict, random_seed=seed)
            res = mgr.run_experiment(exp.experiment_id)

            st.session_state["latest_lab_exp"] = res
            st.success(f"Experiment Created & Executed: {res['experiment_id']}")

    with col2:
        st.subheader("Experiment Summary")
        if "latest_lab_exp" in st.session_state:
            res = st.session_state["latest_lab_exp"]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Experiment ID", res["experiment_id"])
            m2.metric("Config Hash", res["configuration_hash"])
            m3.metric("Sharpe Ratio", f"{res['metrics']['sharpe_ratio']:.2f}")
            m4.metric("Status", res["status"])

            st.markdown("#### Immutable Configuration Snapshot")
            st.json({
                "dataset_id": res["dataset_id"],
                "feature_version": res["feature_version"],
                "model_version": res["model_version"],
                "hypothesis": res["hypothesis"]
            })

with tabs[1]:
    st.subheader("Experiment Runs & Metric Store")
    if "latest_lab_exp" in st.session_state:
        res = st.session_state["latest_lab_exp"]
        st.dataframe(pd.DataFrame([res["metrics"]]), use_container_width=True)

        st.markdown("#### Registered Artifacts")
        st.json(res["run"].get("artifacts", {}))
    else:
        st.info("Execute an experiment to view runs and metric store.")

with tabs[2]:
    st.subheader("End-to-End Lineage DAG Graph")
    if "latest_lab_exp" in st.session_state:
        res = st.session_state["latest_lab_exp"]
        lineage = res["lineage"]["lineage_dag"]
        st.dataframe(pd.DataFrame(lineage), use_container_width=True)
    else:
        st.info("Execute an experiment to view lineage graph.")

with tabs[3]:
    st.subheader("Research Knowledge Base & Findings Index")
    findings = list(mgr.knowledge_base.findings.values())
    if findings:
        st.dataframe(pd.DataFrame([f.to_dict() for f in findings]), use_container_width=True)
    else:
        st.info("No findings indexed in knowledge base yet.")

with tabs[4]:
    st.subheader("Replication & Reproducibility Verification")
    if "latest_lab_exp" in st.session_state:
        res = st.session_state["latest_lab_exp"]
        if st.button("Run Replication Verification"):
            rep_res = mgr.replicate_experiment(res["experiment_id"])
            st.json(rep_res)
    else:
        st.info("Execute an experiment to run replication verification.")
