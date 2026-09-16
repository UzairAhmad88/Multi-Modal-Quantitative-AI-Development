"""
QUANT AI Workspace — Page 35: Model Monitoring & Research Health OS Dashboard.
Provides interactive health score, data drift PSI metrics, DDM concept drift timeline, alpha decay curves, and alert logs.
"""

import streamlit as st
import pandas as pd
import numpy as np

from monitoring.services.monitoring_service import MonitoringService
from monitoring.reports.generator import MonitoringReportGenerator

st.set_page_config(page_title="Model Monitoring OS", layout="wide")

st.title("👁️ Model Monitoring & Research Health OS")
st.caption("Real-Time Data Drift, Feature Shift, Prediction Drift, Concept Drift, Alpha Decay & Research Integrity Health Dashboard")

st.info("🔒 **RESEARCH ONLY & NO-LIVE-TRADING SAFETY**: All drift alerts, health scores, and decay indicators are for quantitative model diagnostics and adaptive monitoring. Live trading remains strictly disabled.")

# Sidebar Configuration
st.sidebar.header("⚙️ Monitoring Configuration")
experiment_id = st.sidebar.text_input("Experiment ID", "EXP-MONITOR-001")
psi_warn = st.sidebar.slider("PSI Warning Threshold", 0.05, 0.25, 0.10, 0.01)
psi_crit = st.sidebar.slider("PSI Critical Threshold", 0.15, 0.50, 0.25, 0.01)

service = MonitoringService()

if st.sidebar.button("🚀 Run Model Monitoring Audit"):
    with st.spinner("Auditing data drift, concept drift, alpha decay, and research health score..."):
        res = service.run_monitoring(experiment_id=experiment_id)
        st.session_state["mon_result"] = res
        st.success(f"Monitoring Audit Complete: {res.monitoring_id}")

res = st.session_state.get("mon_result")

if not res:
    res = service.run_monitoring(experiment_id=experiment_id)
    st.session_state["mon_result"] = res

health = res.health_score

# Top Health Score Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Overall Health", f"{health.overall_health_score:.1f}", delta=health.status)
col2.metric("Data Quality", f"{health.data_quality_score:.1f}")
col3.metric("Feature Stability", f"{health.feature_stability_score:.1f}")
col4.metric("Concept Stability", f"{health.concept_stability_score:.1f}")
col5.metric("Alpha Retention", f"{health.alpha_retention_score:.1f}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Drift Audit", "📉 Concept & Alpha Decay", "🚨 Active Alerts", "📑 Markdown Report"])

with tab1:
    st.subheader("Multi-Feature Data Drift Audit (PSI, KS & Wasserstein)")
    if res.data_drift_results:
        drift_data = []
        for d in res.data_drift_results:
            drift_data.append({
                "Feature": d.feature_name,
                "PSI Score": round(d.psi_score, 4),
                "KS Statistic": round(d.ks_statistic, 4),
                "KS p-value": round(d.ks_pvalue, 4),
                "Wasserstein Dist": round(d.wasserstein_distance, 4),
                "Severity": d.severity,
                "Is Drifted": d.is_drifted,
            })
        df_drift = pd.DataFrame(drift_data)
        st.dataframe(df_drift, use_container_width=True)

        st.bar_chart(df_drift.set_index("Feature")["PSI Score"])
    else:
        st.info("No data drift metrics available.")

with tab2:
    st.subheader("Concept Drift & Alpha IC Decay")
    c1, c2 = st.columns(2)

    with c1:
        st.write("#### Concept Drift Detectors")
        if res.concept_drift_results:
            for cd in res.concept_drift_results:
                status_icon = "🔴 DRIFT" if cd.drift_detected else ("🟡 WARN" if cd.warning_detected else "🟢 STABLE")
                st.write(f"- **Method `{cd.method}`**: {status_icon} (Current: `{cd.current_value:.4f}`, Change-Point: `{cd.change_point_index}`)")
        else:
            st.info("No concept drift data available.")

    with c2:
        st.write("#### Alpha IC Decay & Rolling Sharpe")
        if res.alpha_decay:
            ad = res.alpha_decay
            st.write(f"- **Rolling Lag-1 IC**: `{ad.rolling_ic:.4f}`")
            st.write(f"- **Rank IC**: `{ad.rank_ic:.4f}`")
            st.write(f"- **IC Half-Life**: `{ad.ic_half_life_days:.1f} days`")
            st.write(f"- **IC Decay %**: `{ad.ic_decay_pct:.2%}`")
            st.write(f"- **Rolling Sharpe**: `{ad.rolling_sharpe:.2f}`")
        else:
            st.info("No alpha decay data available.")

with tab3:
    st.subheader("Active Monitoring Alerts & Diagnostic Evidence")
    if res.alerts:
        for alert in res.alerts:
            sev_color = "red" if alert.severity == "CRITICAL" else ("orange" if alert.severity == "WARNING" else "blue")
            st.markdown(f":{sev_color}[**[{alert.severity}] {alert.component}**: {alert.message}]")
    else:
        st.success("No active alerts triggered. Research system operating cleanly!")

with tab4:
    st.subheader("Generated Monitoring & Research Health Report")
    generator = MonitoringReportGenerator()
    report_md = generator.generate_markdown_report(res)
    st.text_area("Markdown Report", report_md, height=400)
    st.download_button("📥 Download Report.md", report_md, file_name=f"{res.monitoring_id}_report.md")
