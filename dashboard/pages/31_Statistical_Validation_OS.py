"""
Streamlit Page: Statistical Validation, Significance Testing, Bootstrap & Research Integrity OS.
"""

import streamlit as st
import pandas as pd
import numpy as np

from validation.core.validation_manager import StatisticalValidationManager
from validation.reports.validation_report_generator import ValidationReportGenerator

st.set_page_config(page_title="Statistical Validation OS", page_icon="📊", layout="wide")

mgr = StatisticalValidationManager()

st.title("📊 Statistical Validation & Research Integrity OS")
st.caption("Empirical Block Bootstrap, Parametric & Non-Parametric Significance, Multiple Testing Corrections & Overfitting Diagnostics")

tabs = st.tabs([
    "Validation Engine Runner",
    "Bootstrap Confidence Intervals",
    "Significance & Effect Sizes",
    "Multiple Testing Adjustments",
    "Temporal Stability Windows",
    "Research Integrity & Diagnostics",
])

with tabs[0]:
    st.subheader("Run Statistical Validation Engine")
    col1, col2 = st.columns([1, 2])

    with col1:
        exp_id = st.text_input("Experiment ID", "EXP-MULTIMODAL-001")
        sample_size = st.number_input("Return Series Observations", value=500)
        train_sharpe = st.number_input("Training Period Sharpe Ratio", value=2.10)
        seed = st.number_input("Random Seed", value=42)

        if st.button("Execute Statistical Validation", type="primary"):
            np.random.seed(int(seed))
            returns = np.random.normal(loc=0.0008, scale=0.012, size=int(sample_size))

            val = mgr.run_validation(
                experiment_id=exp_id,
                returns=returns,
                train_sharpe=train_sharpe,
                random_seed=int(seed),
            )
            st.session_state["active_val_id"] = val.validation_id
            st.success(f"Validation Completed: {val.validation_id} (Status: {val.validation_status})")

    with col2:
        st.subheader("Validation Overview")
        if "active_val_id" in st.session_state:
            val = mgr.get_validation(st.session_state["active_val_id"])
            if val:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Validation ID", val.validation_id)
                m2.metric("Status", val.validation_status)
                m3.metric("Sample Size", val.sample_size)
                m4.metric("Config Hash", val.configuration_hash[:8] + "...")

                st.markdown("#### Moments Summary")
                st.dataframe(pd.DataFrame([val.basic_statistics]), use_container_width=True)

with tabs[1]:
    st.subheader("Stationary Block Bootstrap Confidence Intervals")
    if "active_val_id" in st.session_state:
        val = mgr.get_validation(st.session_state["active_val_id"])
        if val:
            boot_data = [b.model_dump() for b in val.bootstrap_results]
            st.dataframe(pd.DataFrame(boot_data), use_container_width=True)

            st.markdown("#### Parametric vs Bootstrap CI")
            st.json({
                "parametric_95_ci": val.confidence_intervals,
                "bootstrap_block_20_ci": boot_data[0] if boot_data else {},
            })
    else:
        st.info("Execute statistical validation to view bootstrap confidence intervals.")

with tabs[2]:
    st.subheader("Significance Testing & Cohen's d Effect Sizes")
    if "active_val_id" in st.session_state:
        val = mgr.get_validation(st.session_state["active_val_id"])
        if val:
            sig_data = [s.model_dump() for s in val.significance_results]
            st.dataframe(pd.DataFrame(sig_data), use_container_width=True)
    else:
        st.info("Execute statistical validation to view hypothesis test results.")

with tabs[3]:
    st.subheader("Multiple Testing Corrections (FWER / FDR)")
    if "active_val_id" in st.session_state:
        val = mgr.get_validation(st.session_state["active_val_id"])
        if val and val.multiple_testing_result:
            mt = val.multiple_testing_result.model_dump()
            st.json(mt)
    else:
        st.info("Execute statistical validation to view multiple testing adjustments.")

with tabs[4]:
    st.subheader("Temporal Stability & Subperiod Windows")
    if "active_val_id" in st.session_state:
        val = mgr.get_validation(st.session_state["active_val_id"])
        if val and val.stability_result:
            st.metric("Stability Score", f"{val.stability_result.stability_score} / 100")
            st.dataframe(pd.DataFrame([w.model_dump() for w in val.stability_result.subperiods]), use_container_width=True)
    else:
        st.info("Execute statistical validation to view stability subperiods.")

with tabs[5]:
    st.subheader("Research Integrity & Overfitting Diagnostics")
    if "active_val_id" in st.session_state:
        val = mgr.get_validation(st.session_state["active_val_id"])
        if val:
            st.markdown("#### Assumption Checks")
            st.dataframe(pd.DataFrame([c.model_dump() for c in val.assumption_checks]), use_container_width=True)

            st.markdown("#### Research Integrity Flags")
            if val.integrity_flags:
                st.dataframe(pd.DataFrame([f.model_dump() for f in val.integrity_flags]), use_container_width=True)
            else:
                st.success("No research integrity warnings or critical flags raised.")
    else:
        st.info("Execute statistical validation to view research integrity diagnostics.")
