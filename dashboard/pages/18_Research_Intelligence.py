"""
Streamlit Dashboard: 18_Research_Intelligence.py
Phase 11: Research Intelligence, Experiment Automation, Model Discovery & Quant Research Assistant.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import sys

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_intelligence.orchestration.pipeline import ResearchIntelligencePipeline
from research_intelligence.hypothesis.registry import HypothesisState
from research_intelligence.experiment_manager.manager import ExperimentConfig, ExperimentPriority
from research_intelligence.comparison.comparator import ExperimentComparator

st.set_page_config(
    page_title="Research Intelligence | Quant AI",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style,
    .main-header { font-size: 2.2rem; font-weight: 700; color: #4F46E5; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #6B7280; margin-bottom: 1.5rem; }
    .metric-card { background: #1E293B; border-radius: 8px; padding: 1rem; border: 1px solid #334155; }
    .badge-supported { background-color: #10B981; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
    .badge-running { background-color: #3B82F6; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
    .badge-rejected { background-color: #EF4444; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🧠 Research Intelligence & Experiment Automation</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Institutional Quant Assistant • Hypothesis Management • Automated Ablation & Robustness • Lineage</div>', unsafe_allow_html=True)

# Initialize Session State Pipeline
if "pipeline" not in st.session_state:
    st.session_state.pipeline = ResearchIntelligencePipeline()
    # Populate initial baseline experiment
    st.session_state.pipeline.run_full_research_workflow(
        title="Multi-Modal Transformer Alpha Boost",
        description="Evaluate sentiment feature addition to market momentum baseline",
        research_question="Does NLP news sentiment increase 5D Sharpe ratio?",
        expected_effect="Sharpe increase by +0.3",
        null_hypothesis="No Sharpe change",
        variables=["market_return", "news_sentiment", "pe_ratio"],
        dataset="market_sp500",
        features=["market_return", "news_sentiment", "pe_ratio"],
        model="Transformer",
    )

pipe: ResearchIntelligencePipeline = st.session_state.pipeline

# Overview KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)
hypos = pipe.hypothesis_registry.list_hypotheses()
exps = pipe.experiment_manager.list_all()
findings = list(pipe.research_memory._findings.values())
failures = pipe.research_memory.list_failures()

with col1:
    st.metric("Hypotheses", len(hypos))
with col2:
    st.metric("Experiments", len(exps))
with col3:
    st.metric("Findings", len(findings))
with col4:
    st.metric("Failures Logged", len(failures))
with col5:
    st.metric("Real Trading", "DISABLED 🔒")

st.divider()

tabs = st.tabs([
    "📋 Hypothesis Registry",
    "⚡ Experiment Runner & Queue",
    "⚖️ Comparison Engine",
    "🔬 Ablation & Robustness",
    "🔍 Error Diagnostics",
    "🕸️ Lineage & Memory",
    "💡 Research Assistant",
])

# TAB 1: Hypothesis Registry
with tabs[0]:
    st.subheader("Hypothesis Pre-Registration & Lifecycle")
    with st.expander("➕ Register New Hypothesis (Pre-Registration)", expanded=False):
        with st.form("new_hypo_form"):
            title = st.text_input("Title", "Cross-Asset Volatility Regime Filter")
            desc = st.text_area("Description / Objective", "Test whether adding VIX regime filter reduces max drawdown.")
            rq = st.text_input("Research Question", "Does VIX regime filtering lower tail drawdown?")
            expected = st.text_input("Expected Effect", "Drawdown reduction > 3%")
            null_h = st.text_input("Null Hypothesis", "No drawdown change")
            dataset = st.selectbox("Dataset", ["market_sp500", "tech_nasdaq", "crypto_top10"])
            features = st.multiselect("Variables / Features", ["market_return", "vix_index", "news_sentiment", "pe_ratio"], ["market_return", "vix_index"])
            submit = st.form_submit_button("Register Hypothesis")
            if submit:
                hypo = pipe.hypothesis_registry.register(
                    title=title,
                    description=desc,
                    research_question=rq,
                    expected_effect=expected,
                    null_hypothesis=null_h,
                    variables=features,
                    dataset=dataset,
                    time_period="2021-2026",
                )
                st.success(f"Hypothesis {hypo.hypothesis_id} registered cleanly!")
                st.rerun()

    hypo_data = []
    for h in pipe.hypothesis_registry.list_hypotheses():
        hypo_data.append({
            "ID": h.hypothesis_id,
            "Title": h.title,
            "Dataset": h.dataset,
            "Status": h.status.value,
            "Variables": ", ".join(h.variables),
            "Registered At": h.created_at[:16],
        })
    st.dataframe(pd.DataFrame(hypo_data), use_container_width=True)

# TAB 2: Experiment Runner & Queue
with tabs[1]:
    st.subheader("Automated Experiment Queue & Execution")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("#### Create New Experiment")
        if hypos:
            hypo_id_sel = st.selectbox("Select Target Hypothesis", [h.hypothesis_id for h in hypos])
            exp_name = st.text_input("Experiment Name", "EXP_LSTM_Sentiment")
            exp_model = st.selectbox("Model Architecture", ["LSTM", "GRU", "Transformer", "XGBoost", "TabNet"])
            exp_feats = st.multiselect("Features", ["market_return", "news_sentiment", "pe_ratio", "vix_index"], ["market_return", "news_sentiment"])
            exp_prio = st.selectbox("Priority", ["LOW", "NORMAL", "HIGH"], index=1)
            auto_app = st.checkbox("Require Human Approval", value=False)

            if st.button("Queue Experiment"):
                cfg = ExperimentConfig(
                    name=exp_name,
                    hypothesis_id=hypo_id_sel,
                    dataset="market_sp500",
                    features=exp_feats,
                    model=exp_model,
                )
                rec = pipe.experiment_manager.create_experiment(
                    cfg, priority=ExperimentPriority(exp_prio), auto_approve=not auto_app
                )
                st.info(f"Experiment {rec.experiment_id} queued! Approved: {rec.approved_by_human}")
                st.rerun()

    with col_b:
        st.markdown("#### Experiment Execution Center")
        exps_all = pipe.experiment_manager.list_all()
        if exps_all:
            selected_exp_id = st.selectbox("Select Experiment to Execute / Inspect", [e.experiment_id for e in exps_all])
            exp_rec = pipe.experiment_manager.get(selected_exp_id)
            
            if exp_rec:
                st.json(exp_rec.to_dict())
                c1, c2 = st.columns(2)
                with c1:
                    if not exp_rec.approved_by_human:
                        if st.button("Approve (Human Review Pass)"):
                            pipe.experiment_manager.approve_experiment(selected_exp_id)
                            st.success("Experiment Approved!")
                            st.rerun()
                with c2:
                    if st.button("Execute Experiment Pipeline"):
                        res = pipe.experiment_runner.run_experiment(selected_exp_id, force_rerun=True)
                        st.success("Execution Complete!")
                        st.json(res)
                        st.rerun()

# TAB 3: Comparison Engine
with tabs[2]:
    st.subheader("Controlled Multi-Metric Experiment Comparator")
    exps_completed = [e for e in pipe.experiment_manager.list_all() if e.results]
    if len(exps_completed) >= 2:
        exp1_id = st.selectbox("Experiment A", [e.experiment_id for e in exps_completed], index=0)
        exp2_id = st.selectbox("Experiment B", [e.experiment_id for e in exps_completed], index=1)
        
        if st.button("Run Side-by-Side Comparison"):
            e1 = pipe.experiment_manager.get(exp1_id)
            e2 = pipe.experiment_manager.get(exp2_id)
            comp = ExperimentComparator.compare(e1, e2)
            st.markdown(f"**Summary:** {comp['summary_statement']}")
            st.json(comp)
    else:
        st.info("Execute at least 2 experiments to run side-by-side comparison.")

# TAB 4: Ablation & Robustness
with tabs[3]:
    st.subheader("Automated Modality Ablation & Robustness Stress Laboratory")
    if exps_completed:
        target_exp = st.selectbox("Target Experiment for Stress Suite", [e.experiment_id for e in exps_completed])
        rec = pipe.experiment_manager.get(target_exp)

        col_ab, col_rob = st.columns(2)
        with col_ab:
            st.markdown("#### Feature Set Modality Ablation")
            if st.button("Run Automated Ablation Study"):
                ab_res = pipe.ablation_engine.run_ablation_study(rec.config, rec.config.hypothesis_id)
                st.success("Ablation Study Complete!")
                st.json(ab_res)

        with col_rob:
            st.markdown("#### Parameter & Market Robustness Stress")
            if st.button("Run Robustness Stress Tests"):
                rob_res = pipe.robustness_engine.run_robustness_suite(rec.config, rec.config.hypothesis_id)
                st.success("Robustness Suite Complete!")
                st.json(rob_res)

# TAB 5: Diagnostics & Error Analysis
with tabs[4]:
    st.subheader("Diagnostic Error Analyzer & Confidence Calibration")
    if exps_completed:
        diag_exp_id = st.selectbox("Select Experiment for Error Analysis", [e.experiment_id for e in exps_completed], key="diag_exp")
        exp_diag_rec = pipe.experiment_manager.get(diag_exp_id)

        if st.button("Run Diagnostic Analyzer"):
            diag_output = pipe.error_analyzer.analyze_experiment_errors(
                diag_exp_id, exp_diag_rec.config.features
            )
            st.json(diag_output)

# TAB 6: Lineage & Memory
with tabs[5]:
    st.subheader("Research Lineage Graph & Knowledge Base Memory")
    graph_data = pipe.research_memory.get_graph_data()
    st.markdown("#### Knowledge Graph Nodes & Edges")
    st.json(graph_data)

    st.markdown("#### Stored Verified Research Findings")
    f_list = [f.to_dict() for f in pipe.research_memory._findings.values()]
    st.dataframe(pd.DataFrame(f_list) if f_list else pd.DataFrame())

# TAB 7: Research Assistant & Report Generator
with tabs[6]:
    st.subheader("AI Research Recommendation Engine & Markdown Report Downloader")
    if exps_completed:
        asst_exp_id = st.selectbox("Select Experiment for AI Assistant Review", [e.experiment_id for e in exps_completed], key="asst_exp")
        exp_asst_rec = pipe.experiment_manager.get(asst_exp_id)

        st.markdown("#### Automated Research Suggestions")
        recs = pipe.recommendation_engine.generate_recommendations(exp_asst_rec)
        for r in recs:
            st.info(f"**[{r['category']}]** {r['recommendation']}\n\n*Rationale:* {r['rationale']}\n\n*{r['disclaimer']}*")

        st.divider()
        st.markdown("#### Markdown Research Report Generation")
        if st.button("Generate & Download Markdown Report"):
            report_path = pipe.report_generator.generate_experiment_report(exp_asst_rec)
            st.success(f"Report generated at: `{report_path}`")
            with open(report_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            st.download_button(
                label="📥 Download Experiment Report (.md)",
                data=md_content,
                file_name=f"experiment_report_{exp_asst_rec.experiment_id}.md",
                mime="text/markdown",
            )
