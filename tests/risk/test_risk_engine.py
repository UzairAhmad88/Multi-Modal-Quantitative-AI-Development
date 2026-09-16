"""
Unit & Integration Test Suite for Phase 26 Advanced Quantitative Risk & Stress Testing Engine OS.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from api.main import app

from risk.core.risk_engine import AdvancedRiskEngine
from risk.core.risk_snapshot import RiskSnapshot
from risk.market.volatility import VolatilityAnalyzer
from risk.market.beta import BetaCalculator
from risk.market.correlation import CorrelationAnalyzer
from risk.market.covariance import CovarianceAudit
from risk.market.factor import FactorRiskEngine
from risk.portfolio.contribution import RiskContributionEngine
from risk.portfolio.concentration import ConcentrationRiskAnalyzer
from risk.portfolio.exposure import ExposureRiskEngine
from risk.tail.var import VaREngine
from risk.tail.cvar import CVaREngine
from risk.tail.tail_distribution import DrawdownAnalyzer
from risk.scenarios.registry import ScenarioRegistry
from risk.stress.historical import HistoricalStressEngine
from risk.stress.hypothetical import HypotheticalStressEngine
from risk.stress.engine import StressTestingEngine
from risk.monte_carlo.engine import MonteCarloRiskEngine
from risk.diagnostics.limits import RiskLimitEngine
from risk.services.risk_service import RiskService

client = TestClient(app)


def test_volatility_analyzer():
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.015, 200)
    hist_vol = VolatilityAnalyzer.calculate_historical_volatility(returns)
    ewma_vol = VolatilityAnalyzer.calculate_ewma_volatility(returns)

    assert hist_vol > 0
    assert ewma_vol > 0
    assert abs(hist_vol - ewma_vol) < 0.15


def test_beta_calculator():
    np.random.seed(42)
    bench = np.random.normal(0.001, 0.01, 200)
    asset = 1.5 * bench + np.random.normal(0.0, 0.002, 200)  # Beta approx 1.5

    beta = BetaCalculator.calculate_beta(asset, bench)
    assert pytest.approx(beta, 0.2) == 1.5


def test_correlation_and_instability():
    np.random.seed(42)
    rets = np.random.normal(0.001, 0.01, (100, 3))
    diag = CorrelationAnalyzer.compute_correlation_matrix(rets)
    assert "avg_correlation" in diag
    assert len(diag["correlation_matrix"]) == 3

    p1 = np.random.normal(0.001, 0.01, (50, 2))
    p2 = np.random.normal(0.001, 0.01, (50, 2))
    p2[:, 1] = p2[:, 0]  # Force high correlation in p2
    instab = CorrelationAnalyzer.detect_correlation_instability(p1, p2)
    assert "correlation_change_mean" in instab


def test_covariance_audit():
    cov_valid = np.array([[0.04, 0.01], [0.01, 0.04]])
    valid, diag = CovarianceAudit.audit_covariance(cov_valid)
    assert valid is True
    assert diag["is_positive_semidefinite"] is True

    cov_invalid = np.array([[0.04, 0.10], [0.10, 0.04]])  # Non-PSD matrix
    valid, diag = CovarianceAudit.audit_covariance(cov_invalid)
    assert valid is False


def test_risk_contribution_reconciliation():
    weights = {"A": 0.5, "B": 0.5}
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])

    contrib = RiskContributionEngine.compute_contributions(weights, cov)
    assert contrib["reconciled"] is True
    assert pytest.approx(contrib["sum_ccr"], 1e-4) == contrib["portfolio_volatility"]


def test_concentration_risk():
    weights = {"A": 0.5, "B": 0.5}
    conc = ConcentrationRiskAnalyzer.analyze(weights)
    assert conc["hhi"] == 0.5
    assert conc["effective_n"] == 2.0


def test_var_and_cvar_engines():
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 500)

    var_hist = VaREngine.historical_var(returns, confidence_level=0.95)
    var_param = VaREngine.parametric_var(returns, confidence_level=0.95)
    cvar = CVaREngine.calculate_cvar(returns, confidence_level=0.95)

    assert var_hist > 0
    assert var_param > 0
    assert cvar >= var_hist  # CVaR is expected loss beyond VaR


def test_drawdown_analyzer():
    returns = np.array([0.01, 0.02, -0.05, -0.03, 0.04, 0.02])
    dd_res = DrawdownAnalyzer.analyze_drawdown(returns, initial_value=100000.0)

    assert dd_res["max_drawdown"] > 0
    assert len(dd_res["drawdown_events"]) >= 1


def test_scenario_registry():
    registry = ScenarioRegistry(storage_dir="artifacts/test_scenarios")
    scen = registry.get_scenario("MARKET_CRASH_20PCT")
    assert scen is not None
    assert scen["parameters"]["equity_market_shock"] == -0.20


def test_hypothetical_stress_engine():
    weights = {"AAPL": 0.6, "MSFT": 0.4}
    res = HypotheticalStressEngine.run_hypothetical_stress(
        scenario_id="CRASH_10PCT",
        portfolio_id="PORT-TEST",
        weights=weights,
        parameters={"equity_market_shock": -0.10},
        base_value=100000.0,
    )
    assert res.stressed_value == 90000.0
    assert res.absolute_loss == 10000.0
    assert res.percentage_loss == 0.10


def test_monte_carlo_engine_reproducibility():
    engine = MonteCarloRiskEngine(storage_dir="artifacts/test_mc")
    weights = {"A": 0.5, "B": 0.5}
    cov = np.array([[0.04, 0.01], [0.01, 0.04]])

    mc1 = engine.run_simulation("PORT-TEST", weights, cov, num_simulations=2000, random_seed=42)
    mc2 = engine.run_simulation("PORT-TEST", weights, cov, num_simulations=2000, random_seed=42)

    assert mc1["mc_var_95"] == mc2["mc_var_95"]
    assert mc1["mean_pnl"] == mc2["mean_pnl"]


def test_risk_limit_breach_detection():
    limit_engine = RiskLimitEngine({"max_volatility": 0.10, "max_drawdown": 0.05})
    snapshot = {
        "volatility": 0.25,  # Exceeds 10% limit
        "var_95": 0.03,
        "cvar_95": 0.04,
        "maximum_drawdown": 0.15,  # Exceeds 5% limit
        "leverage": 1.0,
    }
    eval_res = limit_engine.evaluate_limits(snapshot)
    assert eval_res["has_breach"] is True
    assert eval_res["status"] == "BREACH_DETECTED"
    assert len(eval_res["breaches"]) == 2


def test_risk_service_full_flow():
    service = RiskService(storage_dir="artifacts/test_risk")
    res = service.run_risk_analysis("PORT-TEST-FULL")

    assert res["risk_id"].startswith("RISK-")
    assert "market_risk" in res
    assert "tail_risk" in res
    assert "monte_carlo_results" in res


def test_risk_api_endpoints():
    res = client.get("/risk-v2/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    run_res = client.post("/risk-v2/run", json={"portfolio_id": "PORT-API-TEST"})
    assert run_res.status_code == 200
    risk_id = run_res.json()["risk_id"]

    var_res = client.get(f"/risk-v2/{risk_id}/var")
    assert var_res.status_code == 200
    assert "tail_risk" in var_res.json()
