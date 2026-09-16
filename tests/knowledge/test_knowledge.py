"""
Unit Tests for Phase 23 Quant Research Knowledge Base & Experiment Intelligence.
"""

import os
import pytest
from knowledge.schemas.knowledge_record import (
    ResearchKnowledgeRecord,
    ResearchClaim,
    ResearchJournalEntry,
    ReproducibilityCard,
    ClaimStatus,
    JournalType,
)
from knowledge.repository.knowledge_repository import KnowledgeRepository
from knowledge.lineage.lineage_service import ResearchLineageService
from knowledge.graph.knowledge_graph import ResearchKnowledgeGraph
from knowledge.embeddings.embedding_provider import EmbeddingProvider
from knowledge.search.search_engine import KnowledgeSearchEngine
from knowledge.comparison.comparison_engine import ExperimentComparisonEngine
from knowledge.summaries.summary_engine import ResearchSummaryEngine
from knowledge.reports.report_generator import KnowledgeReportGenerator


def test_knowledge_repository_crud():
    repo = KnowledgeRepository(base_dir="artifacts/test_knowledge")

    record = ResearchKnowledgeRecord(
        knowledge_id="KNOW-TEST-001",
        experiment_id="EXP-TEST-001",
        dataset_id="DS-SP500",
        feature_set_id="FSET-V1",
        model_id="MDL-XGB",
        strategy_id="STRAT-LS",
        modalities=["market", "news"],
        status="COMPLETED",
        metrics={"sharpe_ratio": 1.55, "cagr": 0.22},
    )

    repo.save_record(record)
    retrieved = repo.get_record("EXP-TEST-001")
    assert retrieved is not None
    assert retrieved.experiment_id == "EXP-TEST-001"
    assert retrieved.metrics["sharpe_ratio"] == 1.55


def test_lineage_service():
    record = ResearchKnowledgeRecord(
        knowledge_id="KNOW-LINEAGE-01",
        experiment_id="EXP-LINEAGE-01",
        dataset_id="DS-SP500",
        feature_set_id="FSET-V1",
        model_id="MDL-LSTM",
        strategy_id="STRAT-TREND",
    )

    lineage = ResearchLineageService.get_experiment_lineage(record)
    assert len(lineage["nodes"]) == 10
    assert len(lineage["edges"]) == 9


def test_knowledge_graph():
    records = [
        ResearchKnowledgeRecord(
            knowledge_id="KNOW-G1",
            experiment_id="EXP-G1",
            dataset_id="DS-SP500",
            feature_set_id="FSET-V1",
            model_id="MDL-XGB",
            strategy_id="STRAT-01",
            report_id="RPT-G1",
        )
    ]
    kg = ResearchKnowledgeGraph()
    kg.build_from_records(records)

    g_dict = kg.to_dict()
    assert g_dict["nodes_count"] >= 4
    assert g_dict["edges_count"] >= 3

    q_res = kg.query_by_node("EXP-G1")
    assert q_res["queried_node"] is not None


def test_embedding_provider_search():
    provider = EmbeddingProvider()
    query = "news sentiment volatile period"
    docs = [
        "market price and volume technical momentum features",
        "news sentiment nlp embeddings during high volatility market regime",
        "fundamental balance sheet ratios quarterly filings",
    ]

    scores = provider.compute_similarity(query, docs)
    assert len(scores) == 3
    # Second doc is most relevant to query
    assert scores[1] > scores[0]
    assert scores[1] > scores[2]


def test_search_engine_and_filters():
    repo = KnowledgeRepository(base_dir="artifacts/test_knowledge_search")
    repo.save_record(
        ResearchKnowledgeRecord(
            knowledge_id="KNOW-SEARCH-1",
            experiment_id="EXP-SEARCH-1",
            dataset_id="DS-SP500",
            feature_set_id="FSET-V1",
            model_id="MDL-TRANSFORMER",
            strategy_id="STRAT-01",
            modalities=["market", "news"],
            status="COMPLETED",
            metrics={"sharpe_ratio": 1.8},
        )
    )

    engine = KnowledgeSearchEngine(repo=repo)

    # Filter search
    res = engine.search(model="transformer", min_sharpe=1.5)
    assert len(res) >= 1
    assert any(r["experiment_id"] == "EXP-SEARCH-1" for r in res)

    # Query search
    res_q = engine.search(query="transformer news")
    assert len(res_q) >= 1


def test_comparison_engine():
    repo = KnowledgeRepository(base_dir="artifacts/test_knowledge")
    rec_a = ResearchKnowledgeRecord(
        knowledge_id="KNOW-COMP-A",
        experiment_id="EXP-COMP-A",
        dataset_id="DS-SP500",
        feature_set_id="FSET-V1",
        model_id="MDL-LSTM",
        strategy_id="STRAT-01",
        modalities=["market"],
        metrics={"sharpe_ratio": 1.2, "cagr": 0.15},
    )
    rec_b = ResearchKnowledgeRecord(
        knowledge_id="KNOW-COMP-B",
        experiment_id="EXP-COMP-B",
        dataset_id="DS-SP500",
        feature_set_id="FSET-V2",
        model_id="MDL-TRANSFORMER",
        strategy_id="STRAT-01",
        modalities=["market", "news"],
        metrics={"sharpe_ratio": 1.6, "cagr": 0.20},
    )
    repo.save_record(rec_a)
    repo.save_record(rec_b)

    engine = ExperimentComparisonEngine(repo=repo)
    comp = engine.compare_experiments("EXP-COMP-A", "EXP-COMP-B")

    assert comp["experiment_a"] == "EXP-COMP-A"
    assert comp["experiment_b"] == "EXP-COMP-B"
    assert len(comp["metrics_comparison"]) >= 2
    # Check warning raised for different modalities
    assert len(comp["warnings"]) >= 1


def test_claims_and_journal_repository():
    repo = KnowledgeRepository(base_dir="artifacts/test_knowledge")

    claim = ResearchClaim(
        claim_id="CLAIM-TEST-01",
        statement="Multi-modal features improve out-of-sample Sharpe ratio",
        status=ClaimStatus.OBSERVED,
    )
    repo.save_claim(claim)
    claims = repo.list_claims()
    assert any(c.claim_id == "CLAIM-TEST-01" for c in claims)

    entry = ResearchJournalEntry(
        journal_id="JRN-TEST-01",
        entry_type=JournalType.OBSERVATION,
        content="Turnover spiked under high volatility regime.",
    )
    repo.save_journal_entry(entry)
    entries = repo.list_journal_entries()
    assert any(e.journal_id == "JRN-TEST-01" for e in entries)


def test_reproducibility_card_and_reports():
    card = ReproducibilityCard(
        card_id="CARD-EXP-TEST",
        experiment_id="EXP-TEST",
        dataset_id="DS-SP500",
        dataset_version="v1.0.0",
        feature_version="FSET-V1",
        model_version="MDL-XGB",
        configuration_hash="SHA256-TEST-HASH",
    )

    md = KnowledgeReportGenerator.generate_reproducibility_card_md(card)
    assert "Reproducibility Card: EXP-TEST" in md
    assert "SHA256-TEST-HASH" in md
