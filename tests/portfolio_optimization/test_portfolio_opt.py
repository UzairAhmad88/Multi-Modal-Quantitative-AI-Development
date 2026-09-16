"""
Unit & Integration Test Suite for Portfolio Optimization, Position Sizing, Risk-Aware Allocation & Portfolio Construction.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
from pathlib import Path

from portfolio_optimization.estimators.expected_returns import ExpectedReturnEstimator
from portfolio_optimization.estimators.covariance import CovarianceEstimator
from portfolio_optimization.constraints.constraint_engine import ConstraintEngine
from portfolio_optimization.objectives.composite_objective import ObjectiveEngine
from portfolio_optimization.optimizers.allocators import (
    EqualWeightAllocator,
    InverseVolatilityAllocator,
    SignalWeightAllocator,
    RiskParityAllocator,
    MeanVarianceOptimizer,
    MinimumVarianceOptimizer,
    TargetVolatilityOptimizer
)
from portfolio_optimization.position_sizing.position_sizer import PositionSizingEngine
from portfolio_optimization.transaction_costs.cost_engine import TransactionCostEngine
from portfolio_optimization.portfolio.rebalancer import RebalancingEngine
from portfolio_optimization.risk.risk_attribution import RiskAttributionEngine
from portfolio_optimization.attribution.performance_attribution import PerformanceAttributionEngine
from portfolio_optimization.scenarios.scenario_engine import ScenarioEngine
from portfolio_optimization.manager import PortfolioOptimizationManager


@pytest.fixture
def sample_assets():
    return ["AAPL", "MSFT", "NVDA", "AMZN"]


@pytest.fixture
def sample_cov():
    return np.array([
        [0.04, 0.01, 0.02, 0.01],
        [0.01, 0.03, 0.01, 0.01],
        [0.02, 0.01, 0.09, 0.02],
        [0.01, 0.01, 0.02, 0.05]
    ])


def test_baseline_allocators(sample_assets, sample_cov):
    eq = EqualWeightAllocator.allocate(sample_assets)
    assert len(eq) == 4
    assert pytest.approx(sum(eq.values()), abs=1e-3) == 1.0
    assert eq["AAPL"] == 0.25

    inv = InverseVolatilityAllocator.allocate(sample_cov, sample_assets)
    assert pytest.approx(sum(inv.values()), abs=1e-3) == 1.0
    assert inv["MSFT"] > inv["NVDA"]  # MSFT has lower variance than NVDA

    sig = SignalWeightAllocator.allocate({"AAPL": 0.8, "MSFT": 0.4, "NVDA": 0.0, "AMZN": -0.2})
    assert pytest.approx(sum(sig.values()), abs=1e-3) == 1.0
    assert sig["AAPL"] > sig["MSFT"]


def test_mathematical_optimizers(sample_assets, sample_cov):
    rp = RiskParityAllocator.allocate(sample_cov, sample_assets)
    assert pytest.approx(sum(rp.values()), abs=1e-3) == 1.0

    min_var = MinimumVarianceOptimizer.allocate(sample_cov, sample_assets)
    assert pytest.approx(sum(min_var.values()), abs=1e-3) == 1.0

    exp_ret = {"AAPL": 0.15, "MSFT": 0.10, "NVDA": 0.25, "AMZN": 0.08}
    mv = MeanVarianceOptimizer.allocate(exp_ret, sample_cov, sample_assets, risk_aversion=2.0)
    assert pytest.approx(sum(mv.values()), abs=1e-3) == 1.0

    targ = TargetVolatilityOptimizer.allocate(rp, sample_cov, sample_assets, target_vol=0.15)
    assert len(targ) == 4


def test_covariance_estimator_and_psd():
    returns_df = pd.DataFrame(np.random.normal(0, 0.01, (100, 3)), columns=["A", "B", "C"])
    cov, assets = CovarianceEstimator.estimate_covariance(returns_df, method="shrinkage")
    assert cov.shape == (3, 3)
    assert assets == ["A", "B", "C"]

    # Test PSD stabilization on negative eigenvalue matrix
    non_psd = np.array([[1.0, 2.0], [2.0, 1.0]])
    psd = CovarianceEstimator.stabilize_psd(non_psd)
    eigs = np.linalg.eigvalsh(psd)
    assert np.all(eigs >= 1e-6)


def test_constraint_engine(sample_assets):
    engine = ConstraintEngine({"long_only": True, "max_weight": 0.35, "max_gross_exposure": 1.0, "max_turnover": 0.50})
    valid_w = {"AAPL": 0.30, "MSFT": 0.30, "NVDA": 0.20, "AMZN": 0.20}
    is_valid, issues = engine.validate_weights(valid_w)
    assert is_valid
    assert not issues

    invalid_w = {"AAPL": 0.50, "MSFT": 0.50, "NVDA": 0.0, "AMZN": 0.0}  # Max weight breach
    is_valid_inv, issues_inv = engine.validate_weights(invalid_w)
    assert not is_valid_inv
    assert len(issues_inv) > 0

    projected = engine.apply_projection(invalid_w)
    assert projected["AAPL"] <= 0.35 + 1e-5


def test_position_sizing_and_kelly():
    k_frac = PositionSizingEngine.calculate_fractional_kelly(win_rate=0.60, win_loss_ratio=1.5, fraction=0.25)
    assert k_frac > 0.0
    assert k_frac < 0.25

    vol_sized = PositionSizingEngine.calculate_volatility_sized_weights({"AAPL": 0.5}, {"AAPL": 0.20})
    assert "AAPL" in vol_sized


def test_transaction_cost_engine():
    cost_eng = TransactionCostEngine(commission_bps=1.0, slippage_bps=5.0, spread_bps=2.0)
    current_w = {"AAPL": 0.20, "MSFT": 0.30}
    target_w = {"AAPL": 0.40, "MSFT": 0.10}
    res = cost_eng.calculate_trade_cost(target_w, current_w, portfolio_value=100000.0)

    assert res["total_trade_volume"] == 40000.0
    assert res["turnover"] == 0.40
    assert res["commission_cost"] == 4.0
    assert res["slippage_cost"] == 20.0
    assert res["spread_cost"] == 8.0
    assert res["total_cost"] == 32.0


def test_rebalancing_engine():
    rebalancer = RebalancingEngine(rebalance_threshold=0.05)
    curr_w = {"AAPL": 0.20, "MSFT": 0.30}
    targ_w = {"AAPL": 0.40, "MSFT": 0.10}
    prices = {"AAPL": 100.0, "MSFT": 200.0}

    orders = rebalancer.generate_rebalance_orders(curr_w, targ_w, prices, portfolio_value=100000.0)
    assert orders["rebalance_required"]
    assert len(orders["orders"]) == 2


def test_risk_and_performance_attribution(sample_assets, sample_cov):
    weights = {"AAPL": 0.25, "MSFT": 0.25, "NVDA": 0.25, "AMZN": 0.25}
    risk_res = RiskAttributionEngine.calculate_risk_contributions(weights, sample_cov)
    assert "portfolio_volatility" in risk_res
    assert len(risk_res["assets"]) == 4

    perf_res = PerformanceAttributionEngine.calculate_asset_attribution(weights, {"AAPL": 0.10, "MSFT": 0.05})
    assert "portfolio_realized_return" in perf_res


def test_scenario_engine(sample_cov):
    weights = {"AAPL": 0.50, "MSFT": 0.50}
    shock = ScenarioEngine.evaluate_market_shock(weights, shock_pct=-0.10)
    assert shock["estimated_impact"] == -0.10

    vol_spike = ScenarioEngine.evaluate_volatility_spike(weights, sample_cov[:2, :2], vol_multiplier=1.5)
    assert vol_spike["shocked_volatility"] > vol_spike["base_volatility"]


def test_portfolio_optimization_manager(sample_assets):
    with tempfile.TemporaryDirectory() as tmp_dir:
        reg_file = str(Path(tmp_dir) / "portfolios.json")
        mgr = PortfolioOptimizationManager(registry_file=reg_file)

        signals = {"AAPL": 0.8, "MSFT": 0.6, "NVDA": 0.4, "AMZN": 0.2}
        res = mgr.optimize_portfolio(alpha_signals=signals, config={"portfolio": {"method": "mean_variance"}})

        assert res["status"] in ["OPTIMAL", "FEASIBLE"]
        assert "portfolio_id" in res
        assert len(mgr.list_portfolios()) == 1
