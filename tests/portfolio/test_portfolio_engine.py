"""
Unit & Integration Test Suite for Phase 25 Portfolio Construction & Optimization Engine OS.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from api.main import app

from portfolio.core.portfolio import Portfolio
from portfolio.core.position import Position
from portfolio.core.weights import WeightValidator
from portfolio.constraints.engine import ConstraintEngine
from portfolio.constraints.position import PositionConstraint
from portfolio.constraints.turnover import TurnoverConstraint
from portfolio.optimization.equal_weight import EqualWeightOptimizer
from portfolio.optimization.signal_weighted import SignalWeightedOptimizer
from portfolio.optimization.min_variance import MinimumVarianceOptimizer
from portfolio.optimization.mean_variance import MeanVarianceOptimizer
from portfolio.optimization.risk_parity import RiskParityOptimizer
from portfolio.optimization.max_diversification import MaximumDiversificationOptimizer
from portfolio.sizing.engine import PositionSizingEngine
from portfolio.costs.transaction import TransactionCostModel
from portfolio.risk.contribution import RiskContributionCalculator
from portfolio.risk.concentration import ConcentrationAnalyzer
from portfolio.risk.attribution import PortfolioRiskAttribution
from portfolio.rebalance.engine import RebalanceEngine
from portfolio.utils.covariance import CovarianceEstimator
from portfolio.utils.lookahead import LookAheadProtector
from portfolio.services.portfolio_service import PortfolioService

client = TestClient(app)


def test_portfolio_object_and_positions():
    port = Portfolio(portfolio_id="PORT-TEST", name="Test Portfolio")
    port.set_weights({"AAPL": 0.6, "MSFT": 0.4})
    assert port.gross_exposure == 1.0
    assert port.net_exposure == 1.0
    assert port.cash_weight == 0.0

    snap = port.create_snapshot()
    assert snap.weights["AAPL"] == 0.6
    assert snap.portfolio_value == 100000.0


def test_weight_validation():
    valid, errors = WeightValidator.validate_weights({"AAPL": 0.5, "MSFT": 0.5})
    assert valid is True
    assert len(errors) == 0

    invalid, errors = WeightValidator.validate_weights({"AAPL": 1.5, "MSFT": -0.2}, long_only=True)
    assert invalid is False
    assert len(errors) >= 1


def test_equal_weight_optimizer():
    opt = EqualWeightOptimizer()
    res = opt.optimize(alpha_scores={"AAPL": 0.0, "MSFT": 0.0, "GOOGL": 0.0})
    assert res.solver_status == "OPTIMAL"
    assert pytest.approx(res.weights["AAPL"], 0.01) == 0.3333


def test_signal_weighted_optimizer():
    opt = SignalWeightedOptimizer()
    res = opt.optimize(alpha_scores={"AAPL": 0.10, "MSFT": 0.05})
    assert res.solver_status == "OPTIMAL"
    assert res.weights["AAPL"] > res.weights["MSFT"]


def test_minimum_variance_optimizer():
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, (200, 3))
    cov = CovarianceEstimator.sample_covariance(returns)

    opt = MinimumVarianceOptimizer({"max_position_weight": 0.60})
    res = opt.optimize(alpha_scores={"A": 0.0, "B": 0.0, "C": 0.0}, cov_matrix=cov)
    assert res.solver_status in ["OPTIMAL", "FEASIBLE"]
    assert max(res.weights.values()) <= 0.601


def test_mean_variance_optimizer():
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, (200, 3))
    cov = CovarianceEstimator.sample_covariance(returns)

    opt = MeanVarianceOptimizer({"risk_aversion": 2.0, "max_position_weight": 0.50})
    res = opt.optimize(alpha_scores={"A": 0.08, "B": 0.02, "C": 0.01}, cov_matrix=cov)
    assert res.solver_status in ["OPTIMAL", "FEASIBLE"]
    assert res.weights["A"] >= res.weights["C"]


def test_risk_parity_optimizer():
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    opt = RiskParityOptimizer()
    res = opt.optimize(alpha_scores={"A": 0.0, "B": 0.0}, cov_matrix=cov)

    assert res.solver_status in ["OPTIMAL", "FEASIBLE"]
    contrib = RiskContributionCalculator.calculate_risk_contributions(
        np.array([res.weights["A"], res.weights["B"]]), cov
    )
    # Risk contributions should be approximately equal
    assert abs(contrib["pcr"]["Asset_0"] - contrib["pcr"]["Asset_1"]) < 0.20


def test_position_limit_constraint():
    cons = PositionConstraint(max_weight=0.10)
    passed, msg = cons.validate({"AAPL": 0.15, "MSFT": 0.85})
    assert passed is False
    assert "exceeds max_position_weight" in msg


def test_turnover_constraint():
    cons = TurnoverConstraint(max_turnover=0.20)
    passed, msg = cons.validate(
        weights={"AAPL": 0.8, "MSFT": 0.2},
        current_weights={"AAPL": 0.5, "MSFT": 0.5},
    )
    assert passed is False
    assert "exceeds max turnover" in msg


def test_transaction_cost_model():
    model = TransactionCostModel(commission_bps=5.0, bid_ask_spread_bps=5.0)
    cost = model.estimate_cost(
        target_weights={"AAPL": 0.6, "MSFT": 0.4},
        current_weights={"AAPL": 0.5, "MSFT": 0.5},
        portfolio_value=100000.0,
    )
    assert cost["total_cost"] > 0
    assert cost["cost_bps"] > 0


def test_risk_attribution_and_concentration():
    weights = {"AAPL": 0.5, "MSFT": 0.5}
    cov = np.eye(2) * 0.04
    attr = PortfolioRiskAttribution.compute_full_attribution(weights, cov)

    assert attr["portfolio_volatility"] > 0
    assert attr["concentration_metrics"]["hhi"] == 0.5
    assert attr["concentration_metrics"]["effective_n"] == 2.0


def test_rebalance_engine():
    engine = RebalanceEngine({"threshold": 0.05})
    trig, reason = engine.evaluate_rebalance_trigger(
        current_weights={"AAPL": 0.5, "MSFT": 0.5},
        target_weights={"AAPL": 0.7, "MSFT": 0.3},
        current_timestamp="2026-09-17T00:00:00Z",
        last_rebalance_timestamp="2026-09-17T00:00:00Z",
    )
    assert trig is True
    assert "THRESHOLD" in reason


def test_lookahead_protector():
    inputs = {
        "signal_1": {"availability_timestamp": "2026-09-15T00:00:00Z"},
        "signal_2": {"availability_timestamp": "2026-09-20T00:00:00Z"},  # Future timestamp
    }
    passed, violations = LookAheadProtector.audit_timestamps(inputs, decision_timestamp="2026-09-17T00:00:00Z")
    assert passed is False
    assert len(violations) == 1


def test_infeasible_constraint_detection():
    engine = ConstraintEngine({
        "max_position_weight": 0.10,  # Max 10% per asset
        "long_only": True,
    })
    # Trying to allocate 100% across 2 assets with 10% limit each is impossible
    eval_res = engine.evaluate_all({"AAPL": 0.50, "MSFT": 0.50})
    assert eval_res["is_feasible"] is False
    assert eval_res["status"] == "INFEASIBLE"


def test_portfolio_service_full_flow():
    service = PortfolioService(storage_dir="artifacts/test_portfolio")
    port = service.create_portfolio("Test Flow", ["AAPL", "MSFT", "GOOGL"])
    assert port.portfolio_id.startswith("PORT-")

    opt = service.optimize_portfolio(port.portfolio_id, method="mean_variance")
    assert opt["solver_status"] in ["OPTIMAL", "FEASIBLE"]
    assert "risk_attribution" in opt


def test_portfolio_api_endpoints():
    res = client.get("/portfolio-v2/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    create_res = client.post("/portfolio-v2/create", json={
        "name": "API Portfolio",
        "assets": ["AAPL", "MSFT"],
        "initial_value": 100000.0,
    })
    assert create_res.status_code == 200
    pid = create_res.json()["portfolio_id"]

    opt_res = client.post("/portfolio-v2/optimize", json={
        "portfolio_id": pid,
        "method": "risk_parity",
    })
    assert opt_res.status_code == 200
    assert "target_weights" in opt_res.json()
