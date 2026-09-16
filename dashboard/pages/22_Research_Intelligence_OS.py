"""
Streamlit Page: Research Intelligence Operating System (Phase 15)
Pattern Discovery, Event Studies, Hypothesis Generator, Research Graph Lineage, Evidence Classifier & NL Assistant.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from research_intelligence.engine import ResearchIntelligenceEngine

st.set_page_config(page_title="Research Intelligence OS", layout="wide")

st.title("🧠 Quant Research Intelligence & Pattern OS")
st.markdown("Evidence-based quantitative pattern discovery, hypothesis generation, research lineage graph, and NL assistant queries.")

engine = ResearchIntelligenceEngine()

tabs = st.tabs([
    "🔍 Pattern Discovery",
    "🧪 Hypothesis Engine",
    "📅 Event Studies & Lags",
    "🕸️ Research Lineage Graph",
    "📚 Evidence & Memory",
    "💬 NL Research Assistant"
])

# TAB 1: Pattern Discovery
with tabs[0]:
    st.header("Automated Multi-Modal Pattern Discovery")
    if st.button("🚀 Execute Pattern Discovery", type="primary"):
        with st.spinner("Scanning market, news, fundamental, and cross-modal series for descriptive patterns..."):
            res = engine.discover_and_hypothesize()

        st.success(f"Discovered {len(res['patterns'])} patterns and {len(res['anomalies'])} anomalies.")

        st.subheader("Discovered Patterns")
        if res["patterns"]:
            st.dataframe(pd.DataFrame(res["patterns"]), use_container_width=True)

        st.subheader("Detected Anomalies & Research Questions")
        if res["anomalies"]:
            st.dataframe(pd.DataFrame(res["anomalies"]), use_container_width=True)

# TAB 2: Hypothesis Engine
with tabs[1]:
    st.header("Structured Research Hypothesis Generator")

    col1, col2 = st.columns(2)
    with col1:
        statement = st.text_area("Hypothesis Statement", value="News sentiment is positively correlated with 5-day cumulative returns.")
        indep_var = st.text_input("Independent Variable", value="news_sentiment")
        dep_var = st.text_input("Dependent Variable", value="returns_5d")
    with col2:
        null_h = st.text_area("Null Hypothesis (H0)", value="No statistically significant relationship exists between news sentiment and returns_5d.")
        alt_h = st.text_area("Alternative Hypothesis (H1)", value="A statistically significant positive correlation exists between news sentiment and returns_5d.")

    if st.button("➕ Generate & Store Hypothesis"):
        from research_intelligence.hypotheses.hypothesis_types import HypothesisType
        hyp = engine.hypothesis_engine.create_hypothesis(
            statement=statement,
            hypothesis_type=HypothesisType.MULTIMODAL,
            independent_variable=indep_var,
            dependent_variable=dep_var,
            null_hypothesis=null_h,
            alternative_hypothesis=alt_h
        )
        st.success(f"Hypothesis Registered! ID: `{hyp.hypothesis_id}`")
        st.code(hyp.to_yaml(), language="yaml")

    st.subheader("Registered Hypotheses")
    hyps = engine.hypothesis_engine.list_hypotheses()
    if hyps:
        st.dataframe(pd.DataFrame([h.to_dict() for h in hyps]), use_container_width=True)

# TAB 3: Event Studies & Lags
with tabs[2]:
    st.header("Event Study & Temporal Lead-Lag Analysis")
    st.markdown("Evaluates pre/post event cumulative returns across event windows `[-1,+1]`, `[-3,+3]`, `[-5,+5]`, `[-10,+10]`.")

    if st.button("📊 Execute Sample Event Study"):
        returns_df = engine.pattern_discovery._generate_synthetic_research_df()
        events = list(returns_df.index[::20])
        res = engine.event_study.analyze_events(returns_df, events)
        st.json(res)

# TAB 4: Research Lineage Graph
with tabs[4]:
    st.header("Research Lineage & Knowledge Memory")
    graph_dict = engine.graph.to_dict()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Research Graph Nodes")
        st.dataframe(pd.DataFrame(graph_dict.get("nodes", [])), use_container_width=True)
    with col_b:
        st.subheader("Research Graph Edges")
        st.dataframe(pd.DataFrame(graph_dict.get("edges", [])), use_container_width=True)

# TAB 5: Evidence & Memory
with tabs[3]:
    st.header("Evidence Classification & Memory Retention")
    findings = engine.memory.get_all_findings()
    if findings:
        st.dataframe(pd.DataFrame(findings), use_container_width=True)
    else:
        st.info("No research findings recorded in persistent memory yet.")

    st.subheader("Failed Hypotheses Knowledge Bank")
    failed = engine.memory.get_failed_hypotheses()
    if failed:
        st.dataframe(pd.DataFrame(failed), use_container_width=True)
    else:
        st.info("No failed hypotheses recorded yet.")

# TAB 6: NL Research Assistant
with tabs[5]:
    st.header("Evidence-Based Natural Language Research Assistant")
    user_q = st.text_input("Ask Research Question", value="Show experiments involving news sentiment.")
    if st.button("💬 Query Research Knowledge Base"):
        res = engine.assistant.query(user_q)
        st.json(res)
