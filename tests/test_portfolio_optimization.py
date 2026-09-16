"""
Unit & Integration Tests for Phase 7 Portfolio Optimization & Risk Engine
Validates expected return models, covariance estimators, 7 portfolio optimizers, risk budgeting,
volatility targeting, portfolio constraints, cost models, and rebalancing events.
"""

import pytest
import numpy as np
import pandas as pd

from src.portfolio.expected_returns import ExpectedReturnModel
from src.portfolio.covariance import CovarianceEstimator
from src.portfolio.optimizers import (
    EqualWeightOptimizer,
    SignalWeightOptimizer,
    InverseVolatilityOptimizer,
    MinimumVarianceOptimizer,
    MeanVarianceOptimizer,
    RiskParityOptimizer,
    HRPOptimizer,
)
from src.portfolio.risk_budgeting import RiskBudgetEngine
from src.portfolio.position_sizing_advanced import VolatilityTargetingEngine, ConfidencePositionSizer
from src.portfolio.constraints import PortfolioConstraintEngine
from src.portfolio.costs import CostModel
from src.portfolio.rebalancer import PortfolioRebalancer


@pytest.fixture
def sample_data():
    symbols = ["AAPL", "NVDA", "MSFT", "AMZN"]
    np.random.seed(42)
    rets = pd.DataFrame(np.random.normal(0.0005, 0.012, (200, 4)), columns=symbols)
    alphas = {"AAPL": 0.03, "NVDA": 0.05, "MSFT": 0.02, "AMZN": 0.01}
    return symbols, rets, alphas


def test_expected_returns_model(sample_data):
    symbols, _, alphas = sample_data
    model = ExpectedReturnModel(method="zscore")
    exp_rets = model.compute_expected_returns(alphas)
    assert len(exp_rets) == 4
    assert "AAPL" in exp_rets


def test_covariance_estimator(sample_data):
    symbols, rets, _ = sample_data
    est = CovarianceEstimator(rets)
    cov_sample = est.compute_sample_covariance()
    cov_ewma = est.compute_ewma_covariance()
    cov_shrunk = est.compute_shrinkage_covariance()

    assert cov_sample.shape == (4, 4)
    assert cov_ewma.shape == (4, 4)
    assert cov_shrunk.shape == (4, 4)

    stability = est.check_stability(cov_shrunk)
    assert stability["is_positive_definite"]


def test_portfolio_optimizers(sample_data):
    symbols, rets, alphas = sample_data
    exp_model = ExpectedReturnModel()
    exp_rets = pd.Series(exp_model.compute_expected_returns(alphas))

    est = CovarianceEstimator(rets)
    cov_df = est.compute_shrinkage_covariance()

    optimizers = [
        EqualWeightOptimizer(0.35),
        SignalWeightOptimizer(0.35),
        InverseVolatilityOptimizer(0.35),
        MinimumVarianceOptimizer(0.35),
        MeanVarianceOptimizer(2.5, 0.35),
        RiskParityOptimizer(0.35),
        HRPOptimizer(0.35),
    ]

    for opt in optimizers:
        w = opt.optimize(exp_rets, cov_df)
        assert len(w) == 4
        assert pytest.approx(w.sum(), 0.02) == 1.0
        assert (w >= -1e-4).all()


def test_risk_budget_engine(sample_data):
    symbols, rets, _ = sample_data
    weights = pd.Series([0.25, 0.25, 0.25, 0.25], index=symbols)
    est = CovarianceEstimator(rets)
    cov_df = est.compute_sample_covariance()

    rb = RiskBudgetEngine(cov_df)
    rb_df = rb.compute_risk_contributions(weights)
    assert "component_risk_crc" in rb_df.columns
    total_crc = rb_df["component_risk_crc"].sum()

    w_val = weights.values.reshape(-1, 1)
    port_vol = np.sqrt(float((w_val.T @ cov_df.values @ w_val).item()))
    assert pytest.approx(total_crc, 0.01) == port_vol


def test_volatility_targeting(sample_data):
    symbols, rets, alphas = sample_data
    weights = pd.Series([0.25, 0.25, 0.25, 0.25], index=symbols)
    est = CovarianceEstimator(rets)
    cov_df = est.compute_sample_covariance()

    vol_engine = VolatilityTargetingEngine(target_volatility_ann=0.15, max_leverage=1.0)
    scaled_w, mult = vol_engine.scale_portfolio(weights, cov_df)
    assert len(scaled_w) == 4
    assert mult > 0


def test_portfolio_constraint_engine():
    engine = PortfolioConstraintEngine(max_asset_weight=0.25, rebalance_threshold=0.02)
    target_w = pd.Series({"AAPL": 0.40, "NVDA": 0.30, "MSFT": 0.15, "AMZN": 0.15})
    curr_w = pd.Series({"AAPL": 0.24, "NVDA": 0.25, "MSFT": 0.15, "AMZN": 0.15})

    constrained_w, logs = engine.apply_constraints(target_w, current_weights=curr_w)
    assert constrained_w["AAPL"] <= 0.25
    assert len(logs) > 0


def test_cost_model():
    cm = CostModel(commission_bps=10.0, slippage_bps=5.0)
    cost = cm.compute_trade_cost(trade_value=50000.0)
    assert cost["total_cost"] > 0
    assert cost["commission"] > 0


def test_portfolio_rebalancer():
    rebalancer = PortfolioRebalancer("MeanVariance", "weekly")
    curr_w = pd.Series({"AAPL": 0.20, "NVDA": 0.30})
    targ_w = pd.Series({"AAPL": 0.30, "NVDA": 0.20})

    res = rebalancer.execute_rebalance(curr_w, targ_w)
    assert res["turnover"] == pytest.approx(0.10, 0.01)
    assert res["trade_count"] == 2
