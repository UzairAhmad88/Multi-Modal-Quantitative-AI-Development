"""
Streamlit Page 16: MLOps Registry & Automated Experiment Tracking
Provides visual inspection for Experiment Manager, Model Registry, Feature Registry, Dataset Registry, Lineage Graph, and Reproducibility Engine.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.mlops.experiments import ExperimentManager
from src.mlops.datasets import DatasetRegistry
from src.mlops.features import FeatureRegistry
from src.mlops.models import ModelRegistry
from src.mlops.strategies import StrategyRegistry
from src.mlops.lineage import LineageTracker
from src.mlops.reproducer import ExperimentReproducer

st.set_page_config(page_title="MLOps & Model Registry", page_icon="⚙️", layout="wide")

st.title("⚙️ MLOps & Quant Model Registry Platform")
st.caption("Institutional Automated Quant Research, Model Lifecycle Management & Lineage Traceability")

# Initialize registries
exp_mgr = ExperimentManager()
ds_reg = DatasetRegistry()
feat_reg = FeatureRegistry()
model_reg = ModelRegistry()
strat_reg = StrategyRegistry()
lineage_tr = LineageTracker()

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧪 Experiments", 
    "🤖 Model Registry", 
    "📊 Dataset Registry", 
    "⚡ Feature Registry", 
    "🕸️ Lineage Graph", 
    "🔄 Reproducibility"
])

# 1. EXPERIMENTS TAB
with tab1:
    st.subheader("Automated Experiment Tracking")
    exps = exp_mgr.list_experiments()
    if exps:
        df_exp = pd.DataFrame(exps)
        st.dataframe(df_exp, use_container_width=True)
    else:
        st.info("No active experiments logged. Run `python scripts/run_experiment.py` to initiate an experiment.")

    st.markdown("---")
    st.subheader("Run Experiment Comparison")
    exp_id_input = st.text_input("Enter Run ID to inspect details (e.g., EXP-RUN-001):", "EXP-RUN-001")
    if st.button("Inspect Run Details"):
        exp = exp_mgr.get_experiment(exp_id_input)
        if exp:
            st.json(exp)
        else:
            st.warning(f"Experiment {exp_id_input} not found.")

# 2. MODEL REGISTRY TAB
with tab2:
    st.subheader("Institutional Quant Model Registry")
    models = model_reg.list_models()
    if models:
        df_models = pd.DataFrame(models)
        st.dataframe(df_models, use_container_width=True)
        
        st.markdown("### Model Promotion Workflow")
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_m = st.selectbox("Select Model:", [m["model_id"] for m in models])
        with col2:
            target_status = st.selectbox("Target Lifecycle Status:", ["VALIDATED", "PAPER", "ARCHIVED"])
        with col3:
            if st.button("Update Model Status"):
                updated = model_reg.update_status(selected_m, target_status)
                st.success(f"Model {selected_m} promoted to status: {updated['status']}")
                st.rerun()
    else:
        st.info("No models registered yet.")

# 3. DATASET REGISTRY TAB
with tab3:
    st.subheader("Dataset Registry & Quality Audit")
    datasets = ds_reg.list_datasets()
    if datasets:
        df_ds = pd.DataFrame(datasets)
        st.dataframe(df_ds, use_container_width=True)
    else:
        st.info("No datasets registered yet.")

# 4. FEATURE REGISTRY TAB
with tab4:
    st.subheader("Feature Registry & Transformation Lineage")
    features = feat_reg.list_features()
    if features:
        df_feat = pd.DataFrame(features)
        st.dataframe(df_feat, use_container_width=True)
    else:
        st.info("No features registered yet.")

# 5. LINEAGE GRAPH TAB
with tab5:
    st.subheader("End-to-End Research Lineage Graph")
    st.markdown("""
    **Lineage Traceability Pipeline**:
    `DATASET` ➔ `FEATURE VERSION` ➔ `CONFIG` ➔ `MODEL VERSION` ➔ `ALPHA` ➔ `PORTFOLIO` ➔ `RISK` ➔ `BACKTEST` ➔ `PAPER SESSION`
    """)
    run_id_lineage = st.text_input("Enter Run ID for Lineage Graph:", "EXP-RUN-001")
    if st.button("Generate Lineage Tree"):
        graph = lineage_tr.get_lineage(run_id_lineage)
        if graph:
            st.json(graph)
        else:
            st.warning(f"No lineage graph found for {run_id_lineage}.")

# 6. REPRODUCIBILITY TAB
with tab6:
    st.subheader("Deterministic Experiment Reproducer")
    repro_id = st.text_input("Run ID to Reproduce:", "EXP-RUN-001")
    if st.button("Execute Reproducibility Check"):
        repro = ExperimentReproducer()
        with st.spinner("Reproducing experiment environment, features, and model outputs..."):
            res = repro.reproduce(repro_id)
            st.success(f"Reproduction Check Result: {res.get('match_status')}")
            st.json(res)
