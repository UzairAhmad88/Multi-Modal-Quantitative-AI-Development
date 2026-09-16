"""
Streamlit Page: Quant Research Knowledge Base, Experiment Intelligence & Knowledge Graph OS.
"""

import streamlit as st
import pandas as pd
import json

from knowledge.repository.knowledge_repository import KnowledgeRepository
from knowledge.search.search_engine import KnowledgeSearchEngine
from knowledge.comparison.comparison_engine import ExperimentComparisonEngine
from knowledge.graph.knowledge_graph import ResearchKnowledgeGraph
from knowledge.summaries.summary_engine import ResearchSummaryEngine
from knowledge.schemas.knowledge_record import ResearchClaim, ResearchJournalEntry, ClaimStatus, JournalType
from knowledge.reports.report_generator import KnowledgeReportGenerator

st.set_page_config(page_title="Quant Research Knowledge OS", page_icon="🧠", layout="wide")

repo = KnowledgeRepository()
search_engine = KnowledgeSearchEngine(repo=repo)
comp_engine = ExperimentComparisonEngine(repo=repo)
summary_engine = ResearchSummaryEngine(repo=repo)

st.title("🧠 Quant Research Knowledge & Experiment Intelligence OS")
st.caption("Evidence-Driven Experiment Memory, Lineage DAGs, Semantic Search, Controlled Comparisons & Reproducibility Cards")

tabs = st.tabs([
    "Multi-Faceted & Semantic Search",
    "Side-by-Side Experiment Comparison",
    "Interactive Knowledge Graph",
    "Research Journal & Claims",
    "Failure Memory Explorer",
    "Reproducibility Cards & Lineage",
])

with tabs[0]:
    st.subheader("Multi-Faceted & Semantic Vector Search Engine")
    col1, col2 = st.columns([1, 2])

    with col1:
        query = st.text_input("Semantic Free-Text Query", "news sentiment volatile periods")
        model_filter = st.text_input("Model Filter (e.g. xgboost, lstm, transformer)", "")
        status_filter = st.selectbox("Status Filter", ["ALL", "COMPLETED", "FAILED"])
        min_sharpe = st.number_input("Min Sharpe Ratio Filter", value=0.0)

        if st.button("Search Knowledge Base", type="primary"):
            status_val = None if status_filter == "ALL" else status_filter
            results = search_engine.search(
                query=query if query.strip() else None,
                model=model_filter if model_filter.strip() else None,
                status=status_val,
                min_sharpe=min_sharpe if min_sharpe > 0 else None,
            )
            st.session_state["search_results"] = results
            st.success(f"Found {len(results)} matching records.")

    with col2:
        st.subheader("Search Results")
        if "search_results" in st.session_state and st.session_state["search_results"]:
            res = st.session_state["search_results"]
            table_data = [
                {
                    "Experiment ID": r["experiment_id"],
                    "Model": r["model_id"],
                    "Dataset": r["dataset_id"],
                    "Modalities": ", ".join(r.get("modalities", [])),
                    "Status": r["status"],
                    "Sharpe": r.get("metrics", {}).get("sharpe_ratio", "N/A"),
                    "Relevance": r.get("relevance_score", 1.0),
                }
                for r in res
            ]
            st.dataframe(pd.DataFrame(table_data), use_container_width=True)
        else:
            st.info("Execute a search to view matched experiment records.")

with tabs[1]:
    st.subheader("Side-by-Side Controlled Experiment Comparison")
    records = repo.list_records()
    exp_ids = [r.experiment_id for r in records]

    if len(exp_ids) >= 2:
        c1, c2 = st.columns(2)
        with c1:
            exp_a = st.selectbox("Select Experiment A", exp_ids, index=0)
        with c2:
            exp_b = st.selectbox("Select Experiment B", exp_ids, index=1 if len(exp_ids) > 1 else 0)

        if st.button("Compare Experiments", type="primary"):
            comp_res = comp_engine.compare_experiments(exp_a, exp_b)
            st.session_state["active_comp_res"] = comp_res

        if "active_comp_res" in st.session_state:
            comp_res = st.session_state["active_comp_res"]
            if comp_res.get("warnings"):
                for w in comp_res["warnings"]:
                    st.warning(f"⚠️ Comparability Warning: {w}")

            st.markdown("#### Metrics Comparison & Deltas")
            st.dataframe(pd.DataFrame(comp_res["metrics_comparison"]), use_container_width=True)

            st.markdown("#### Configuration Differences")
            st.json(comp_res["configuration_diff"])
    else:
        st.info("At least 2 index records are required to perform side-by-side comparison.")

with tabs[2]:
    st.subheader("Interactive Research Knowledge Graph")
    records = repo.list_records()
    kg = ResearchKnowledgeGraph()
    kg.build_from_records(records)
    graph_dict = kg.to_dict()

    m1, m2 = st.columns(2)
    m1.metric("Total Graph Nodes", graph_dict["nodes_count"])
    m2.metric("Total Graph Edges", graph_dict["edges_count"])

    st.markdown("#### Knowledge Graph Nodes Index")
    st.dataframe(pd.DataFrame(graph_dict["nodes"]), use_container_width=True)

    st.markdown("#### Knowledge Graph Edges Index")
    st.dataframe(pd.DataFrame(graph_dict["edges"]), use_container_width=True)

with tabs[3]:
    st.subheader("Research Journal & Factual Evidence Claims")
    t1, t2 = st.tabs(["Evidence Claims", "Research Journal"])

    with t1:
        st.markdown("#### Register Evidence Claim")
        claim_stmt = st.text_input("Claim Statement", "Adding news sentiment increased out-of-sample Sharpe ratio")
        claim_status = st.selectbox("Claim Status", ["OBSERVED", "STATISTICAL", "HYPOTHESIS", "UNSUPPORTED", "REJECTED"])

        if st.button("Register Research Claim"):
            claim = ResearchClaim(
                claim_id=f"CLAIM-{pd.Timestamp.now().strftime('%M%S')}",
                statement=claim_stmt,
                status=ClaimStatus(claim_status),
            )
            repo.save_claim(claim)
            st.success(f"Claim Registered: {claim.claim_id}")

        claims = repo.list_claims()
        if claims:
            st.dataframe(pd.DataFrame([c.model_dump() for c in claims]), use_container_width=True)

    with t2:
        st.markdown("#### Add Journal Entry")
        j_content = st.text_area("Journal Observation", "Turnover spiked under high volatility regime.")
        j_type = st.selectbox("Entry Type", ["OBSERVATION", "HYPOTHESIS", "DECISION", "RESULT", "FAILURE", "LIMITATION", "FOLLOW_UP"])

        if st.button("Save Journal Entry"):
            entry = ResearchJournalEntry(
                journal_id=f"JRN-{pd.Timestamp.now().strftime('%M%S')}",
                entry_type=JournalType(j_type),
                content=j_content,
            )
            repo.save_journal_entry(entry)
            st.success(f"Journal Entry Saved: {entry.journal_id}")

        entries = repo.list_journal_entries()
        if entries:
            st.dataframe(pd.DataFrame([e.model_dump() for e in entries]), use_container_width=True)

with tabs[4]:
    st.subheader("Failure Memory Explorer")
    failures = search_engine.search(status="FAILED")
    if failures:
        st.dataframe(pd.DataFrame(failures), use_container_width=True)
    else:
        st.info("No failed experiments recorded in memory.")

with tabs[5]:
    st.subheader("Reproducibility Cards & Lineage Explorer")
    records = repo.list_records()
    if records:
        exp_id_sel = st.selectbox("Select Experiment for Reproducibility Card", [r.experiment_id for r in records])
        card = repo.get_reproducibility_card(exp_id_sel)
        if card:
            md_card = KnowledgeReportGenerator.generate_reproducibility_card_md(card)
            st.markdown(md_card)
    else:
        st.info("No records available to generate Reproducibility Cards.")
