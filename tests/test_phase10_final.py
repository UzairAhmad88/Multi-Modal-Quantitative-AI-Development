"""
Test Suite for Phase 10 Final Quantitative Validation & Production Readiness
Tests System Check, Production Readiness Checker, Data Leakage Auditor,
Baseline Benchmark Engine, Ablation Engine, Robustness Matrix, Claim Validator, and 13-step Demo Pipeline.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.mlops.readiness import ProductionReadinessChecker
from src.research.validation.leakage_audit import DataLeakageAuditor
from src.research.benchmarking.baselines import BenchmarkEngine
from src.research.ablation.ablation_engine import AblationEngine
from src.research.robustness_matrix import RobustnessMatrix
from src.research.claim_validator import ResearchClaimValidator


def test_production_readiness_checker():
    checker = ProductionReadinessChecker()
    audit = checker.audit_production_readiness()
    assert audit["readiness_status"] == "READY"
    assert audit["passed_dimensions"] == 10
    assert audit["failed_dimensions"] == 0


def test_data_leakage_auditor():
    auditor = DataLeakageAuditor()
    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=10),
        "close": 150.0 + np.arange(10),
        "target": np.random.randn(10)
    })
    res = auditor.audit_dataframe(df)
    assert res["has_leakage"] == False
    assert res["audit_status"] == "PASSED"


def test_benchmark_engine():
    engine = BenchmarkEngine()
    df = pd.DataFrame({
        "close": 150.0 + np.cumsum(np.random.randn(50))
    })
    results = engine.evaluate_baselines(df)
    assert len(results) >= 5
    models = [r["model"] for r in results]
    assert "Buy & Hold Benchmark" in models
    assert "MultiModalQuantNet Fusion" in models


def test_ablation_engine():
    ablation = AblationEngine()
    study = ablation.run_ablation_study()
    assert len(study) >= 4
    full_model = study[0]
    assert "Full Multimodal Fusion" in full_model["modality_configuration"]
    assert full_model["sharpe_ratio"] > 1.5


def test_robustness_matrix():
    matrix = RobustnessMatrix()
    cost_res = matrix.evaluate_cost_sensitivity()
    assert len(cost_res) == 5

    reg_res = matrix.evaluate_regime_matrix()
    assert "BULLISH_TREND" in reg_res
    assert reg_res["BULLISH_TREND"]["sharpe_ratio"] > 1.5


def test_research_claim_validator():
    validator = ResearchClaimValidator()
    
    # Compliant text
    text_good = "The model achieved an out-of-sample Sharpe ratio of 1.84 subject to 10 bps transaction costs."
    res_good = validator.audit_text(text_good)
    assert res_good["is_compliant"] == True

    # Non-compliant text
    text_bad = "This algorithm yields a guaranteed return with a risk-free strategy."
    res_bad = validator.audit_text(text_bad)
    assert res_bad["is_compliant"] == False
    assert len(res_bad["violations"]) >= 2
