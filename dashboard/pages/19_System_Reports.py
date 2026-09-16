"""
Streamlit Dashboard: 19_System_Reports.py
Phase 12: Interactive System & Research Report Browser.
"""

import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="System & Research Reports | Quant AI",
    page_icon="📄",
    layout="wide"
)

st.markdown("# 📄 Quantitative Research Reports & Documentation Viewer")
st.markdown("Browse, inspect, and export generated Markdown research reports, experiment summaries, and diagnostic audits.")

reports_dir = Path("reports/research")
if not reports_dir.exists():
    reports_dir.mkdir(parents=True, exist_ok=True)

files = [f.name for f in reports_dir.glob("*.md")]

if not files:
    st.info("No research reports generated yet. Execute an experiment via Research Intelligence to produce reports.")
else:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### Available Reports")
        selected_file = st.radio("Select Report", files)

    with col2:
        if selected_file:
            filepath = reports_dir / selected_file
            st.markdown(f"### Report: `{selected_file}`")
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            st.download_button(
                label="📥 Download Markdown Report",
                data=content,
                file_name=selected_file,
                mime="text/markdown",
            )
            st.divider()
            st.markdown(content)
