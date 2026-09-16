"""
Comprehensive Test Suite for Phase 15 - Quant Research Intelligence & Pattern OS.
"""

import os
import shutil
import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from research_intelligence.discovery.correlation_analyzer import CorrelationAnalyzer
from research_intelligence.discovery.lag_analyzer import LagAnalyzer
from research_intelligence.discovery.anomaly_detector import AnomalyDetectionEngine
from research_intelligence.discovery.pattern_discovery import PatternDiscoveryEngine
from research_intelligence.patterns.event_study import EventStudyEngine
from research_intelligence.patterns.regime_discovery import RegimeDiscoveryEngine
from research_intelligence.hypotheses.hypothesis_engine import HypothesisEngine, HypothesisType
from research_intelligence.experiment_generation.generator import ExperimentGenerator
from research_intelligence.evidence.evidence_engine import EvidenceEngine, EvidenceStatus
from research_intelligence.evidence.research_memory import ResearchMemory
from research_intelligence.attribution.error_analyzer import ModelErrorAnalyzer
from research_intelligence.similarity.similarity import ResearchSimilarityEngine
from research_intelligence.research_graph.graph import ResearchGraph, NodeType, EdgeType
from research_intelligence.utils.assistant import ResearchAssistant
from research_intelligence.engine import ResearchIntelligenceEngine


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_dataset():
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    sentiment = np.random.normal(0.1, 0.5, n)
    returns = 0.4 * sentiment + np.random.normal(0.001, 0.01, n)
    volatility = np.abs(returns) * 2.0 + np.random.normal(0.01, 0.001, n)

    df = pd.DataFrame({
        "news_sentiment": sentiment,
        "returns": returns,
        "volatility": volatility
    }, index=dates)
    return df


def test_correlation_analyzer(sample_dataset):
    ca = CorrelationAnalyzer()
    res = ca.analyze_correlations(sample_dataset, target_col="returns")
    assert res["status"] == "SUCCESS"
    assert len(res["correlations"]) > 0
    top = res["correlations"][0]
    assert "pearson_corr" in top
    assert top["variable"] == "news_sentiment"
    assert top["pearson_corr"] > 0.2


def test_lag_analyzer(sample_dataset):
    la = LagAnalyzer(lags=[0, 1, 5])
    res = la.analyze_lags(sample_dataset, feature_col="news_sentiment", target_col="returns")
    assert res["status"] == "SUCCESS"
    assert len(res["lag_results"]) == 3
    assert res["optimal_lag"] is not None


def test_anomaly_detector(sample_dataset):
    # Inject synthetic anomaly
    sample_dataset.iloc[10, 0] = 100.0  # extreme z-score
    ad = AnomalyDetectionEngine(z_threshold=3.0)
    res = ad.detect_anomalies(sample_dataset)
    assert res["status"] == "SUCCESS"
    assert res["total_anomalies"] >= 1
    assert len(res["research_questions"]) >= 1


def test_event_study(sample_dataset):
    ese = EventStudyEngine()
    events = list(sample_dataset.index[::20])
    res = ese.analyze_events(sample_dataset, events, return_col="returns")
    assert res["status"] == "SUCCESS"
    assert len(res["window_results"]) == 4
    w1 = res["window_results"][0]
    assert w1["window"] == "[-1,+1]"


def test_regime_discovery(sample_dataset):
    rde = RegimeDiscoveryEngine()
    res = rde.analyze_regime_conditions(sample_dataset, feature_col="news_sentiment", target_col="returns")
    assert res["status"] == "SUCCESS"
    assert "HIGH_VOLATILITY" in res["regime_breakdown"]


def test_hypothesis_engine(temp_dir):
    he = HypothesisEngine(storage_dir=temp_dir)
    hyp = he.create_hypothesis(
        statement="News sentiment is associated with returns",
        hypothesis_type=HypothesisType.MULTIMODAL,
        independent_variable="news_sentiment",
        dependent_variable="returns",
        null_hypothesis="No relationship",
        alternative_hypothesis="Significant relationship"
    )
    assert hyp.hypothesis_id.startswith("HYP-")
    loaded = he.get_hypothesis(hyp.hypothesis_id)
    assert loaded is not None
    assert loaded.statement == hyp.statement


def test_experiment_generator(temp_dir):
    he = HypothesisEngine(storage_dir=temp_dir)
    hyp = he.create_hypothesis(
        statement="Test hypothesis",
        hypothesis_type=HypothesisType.MULTIMODAL,
        independent_variable="news_sentiment",
        dependent_variable="returns",
        null_hypothesis="No relationship",
        alternative_hypothesis="Significant relationship"
    )
    eg = ExperimentGenerator(output_dir=temp_dir)
    config = eg.generate_experiment_config(hyp)
    yaml_path = eg.save_experiment_yaml(hyp, config)
    assert Path(yaml_path).exists()
    assert config["experiment"]["hypothesis_id"] == hyp.hypothesis_id


def test_evidence_engine():
    ee = EvidenceEngine()
    metrics = {"sharpe": 1.64, "cagr": 0.187, "max_drawdown": 0.112}
    stats_res = {"p_value": 0.02}
    res = ee.classify_evidence(metrics, stats_res=stats_res)
    assert res["status"] == EvidenceStatus.SUPPORTED.value

    contradicted_metrics = {"sharpe": -0.5, "cagr": -0.10, "max_drawdown": 0.40}
    res2 = ee.classify_evidence(contradicted_metrics, stats_res={"p_value": 0.50})
    assert res2["status"] == EvidenceStatus.CONTRADICTED.value


def test_research_memory(temp_dir):
    mem_file = str(Path(temp_dir) / "memory.json")
    rm = ResearchMemory(memory_file=mem_file)
    rm.record_finding("FND-01", "HYP-01", "EXP-01", "Positive correlation", EvidenceStatus.SUPPORTED.value, {"sharpe": 1.5}, [])
    rm.record_finding("FND-02", "HYP-02", "EXP-02", "Negative return", EvidenceStatus.CONTRADICTED.value, {"sharpe": -0.2}, [])

    findings = rm.get_all_findings()
    assert len(findings) == 2
    failed = rm.get_failed_hypotheses()
    assert len(failed) == 1
    assert failed[0]["hypothesis_id"] == "HYP-02"


def test_model_error_analyzer(sample_dataset):
    mea = ModelErrorAnalyzer()
    preds = sample_dataset["returns"] + np.random.normal(0, 0.005, len(sample_dataset))
    acts = sample_dataset["returns"]
    res = mea.analyze_errors(preds, acts)
    assert res["status"] == "SUCCESS"
    assert "directional_accuracy" in res["metrics"]

    disagreement = mea.analyze_multimodal_disagreement(market_signal=0.5, news_signal=-0.2, fundamental_signal=0.4)
    assert disagreement["consensus_type"] == "PARTIAL_DISAGREEMENT"



def test_research_graph(temp_dir):
    graph_file = str(Path(temp_dir) / "graph.json")
    rg = ResearchGraph(storage_file=graph_file)
    rg.add_node("HYP-01", NodeType.HYPOTHESIS, "Hypothesis 1")
    rg.add_node("EXP-01", NodeType.EXPERIMENT, "Experiment 1")
    rg.add_edge("HYP-01", "EXP-01", EdgeType.TESTED_BY)

    lineage = rg.trace_lineage("EXP-01")
    assert lineage["finding_id"] == "EXP-01"
    assert len(lineage["lineage_chain"]) == 2


def test_research_assistant():
    ra = ResearchAssistant()
    res = ra.query("news sentiment")
    assert "query" in res
    assert "answer" in res
