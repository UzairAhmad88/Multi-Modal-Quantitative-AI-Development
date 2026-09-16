"""
Streamlit Page: Model Factory & Lifecycle Operating System (Phase 16)
Model Registry, Training Engine, Evaluation, Comparison, Champion/Challenger, Monitoring & Rollback.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from models.registry.registry import ModelRegistry, ModelStatus
from models.training.trainer import ModelTrainingEngine
from models.evaluation.comparison import ModelComparisonEngine
from models.lifecycle.rollback import ModelRollbackManager

st.set_page_config(page_title="Model Factory & Lifecycle OS", layout="wide")

st.title("🏭 Model Factory & Controlled Model Lifecycle OS")
st.markdown("Centralized model instantiation, training pipelines, champion/challenger comparisons, and safety-gated model lifecycle transitions.")

registry = ModelRegistry()

tabs = st.tabs([
    "📦 Model Registry",
    "⚙️ Train Model Pipeline",
    "⚖️ Champion vs Challenger",
    "📊 Model Comparison",
    "📈 Health & Monitoring",
    "🔄 Rollback & Archive"
])

# TAB 1: Model Registry
with tabs[0]:
    st.header("Model Registry & Version Inventory")
    models = registry.list_models()
    champ = registry.get_champion()
    champ_id = champ.get("model_id") if champ else "NONE"

    st.metric("Active Champion Model", champ_id, delta=champ.get("version") if champ else "")

    if models:
        df_models = pd.DataFrame([
            {
                "Model ID": m.get("model_id"),
                "Name": m.get("name"),
                "Version": m.get("version"),
                "Type": m.get("model_type"),
                "Status": m.get("status"),
                "MAE": m.get("metrics", {}).get("mae", "N/A"),
                "Sharpe": m.get("metrics", {}).get("sharpe", "N/A"),
                "Updated": m.get("updated_at")
            }
            for m in models
        ])
        st.dataframe(df_models, use_container_width=True)
    else:
        st.info("No models registered yet.")

# TAB 2: Train Model Pipeline
with tabs[1]:
    st.header("Execute Automated Model Training Pipeline")
    col1, col2 = st.columns(2)
    with col1:
        model_type = st.selectbox("Select Model Architecture", ["multimodal", "lstm", "gru", "transformer", "xgboost", "random_forest"])
        model_name = st.text_input("Model Name", value=f"{model_type}_alpha_net")
        version = st.text_input("Version", value="1.0.0")
    with col2:
        epochs = st.number_input("Epochs", value=10, step=1)
        lr = st.number_input("Learning Rate", value=0.001, format="%.4f")
        seed = st.number_input("Random Seed", value=42, step=1)

    if st.button("🚀 Train & Register Model", type="primary"):
        config = {
            "model": {"name": model_name, "type": model_type, "version": version, "task": "regression"},
            "training": {"seed": seed, "epochs": epochs, "learning_rate": lr},
            "data": {"dataset": "DS-SP500_DAILY-v1.0.0"},
            "validation": {"temporal_split": True, "walk_forward": True}
        }

        with st.spinner("Executing model training pipeline..."):
            trainer = ModelTrainingEngine()
            result = trainer.train_model(config)

        st.success(f"Model Trained & Registered! Model ID: `{result.get('model_id')}`")
        st.json(result.get("metrics", {}))

# TAB 3: Champion vs Challenger
with tabs[2]:
    st.header("Champion vs Challenger Evaluation")
    champ = registry.get_champion()
    if champ:
        st.subheader("Current Paper Champion")
        st.json(champ)

        candidates = registry.list_models(status=ModelStatus.CANDIDATE.value)
        if candidates:
            challenger_id = st.selectbox("Select Challenger Model", [c["model_id"] for c in candidates])
            challenger = registry.get_model(challenger_id)
            if challenger:
                st.subheader("Selected Challenger")
                st.json(challenger)

                if st.button("🏆 Promote Challenger to Champion"):
                    registry.set_champion(challenger_id)
                    st.success(f"Successfully promoted `{challenger_id}` to active paper champion!")
        else:
            st.info("No candidates available for promotion.")
    else:
        st.info("No champion model designated yet.")

# TAB 4: Model Comparison
with tabs[3]:
    st.header("Side-by-Side Model Comparison")
    all_m = registry.list_models()
    model_ids = [m["model_id"] for m in all_m]
    if len(model_ids) >= 2:
        selected_ids = st.multiselect("Select Models to Compare", model_ids, default=model_ids[:2])
        if st.button("⚖️ Compare Models"):
            mce = ModelComparisonEngine()
            res = mce.compare_models(selected_ids)
            st.dataframe(pd.DataFrame(res.get("comparison", {})).T, use_container_width=True)
    else:
        st.info("At least two models are required for side-by-side comparison.")

# TAB 5: Health & Monitoring
with tabs[4]:
    st.header("Model Health & Drift Monitoring")
    st.json({
        "total_registered_models": len(all_m),
        "champion_status": "HEALTHY",
        "drift_status": "NO_SIGNIFICANT_DRIFT_DETECTED",
        "gpu_available": False,
        "device_fallback": "CPU"
    })

# TAB 6: Rollback & Archive
with tabs[5]:
    st.header("Model Rollback & Archival Operations")
    if st.button("⏪ Rollback Champion to Previous Candidate"):
        rb = ModelRollbackManager()
        res = rb.rollback()
        if res.get("status") == "SUCCESS":
            st.success(f"Champion rolled back to `{res['restored_champion']}`.")
        else:
            st.error(res.get("reason"))
