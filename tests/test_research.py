"""
Unit & Integration Tests for Phase 5 Research Engine
Validates factor analysis, explainability, sensitivity testing, stress testing, uncertainty, error analysis,
portfolio attribution, and statistical hypothesis testing.
"""

import pytest
import numpy as np
import pandas as pd

from src.research.factor_analysis import FactorAnalyzer
from src.research.explainability import ModelExplainer
from src.research.robustness import RobustnessTester
from src.research.stress_testing import StressTester
from src.research.uncertainty import UncertaintyAnalyzer
from src.research.error_analysis import ErrorAnalyzer
from src.research.attribution import PortfolioAttributor
from src.research.statistical_tests import StatisticalTester
from src.research.runner import ResearchRunner


@pytest.fixture
def sample_market_df():
    dates = pd.date_range(start="2023-01-01", periods=100, freq="B")
    np.random.seed(42)
    price = 100.0 + np.cumsum(np.random.normal(0.1, 1.0, 100))
    df = pd.DataFrame({
        "date": dates,
        "ticker": "AAPL",
        "close": price,
        "volume": np.random.randint(500000, 2000000, 100),
        "sentiment_score": np.random.normal(0.05, 0.3, 100),
        "pe_ratio": 20.0 + np.random.normal(0, 0.5, 100),
        "roe": 0.15 + np.random.normal(0, 0.01, 100),
    })
    df["forward_return"] = df["close"].pct_change(5).shift(-5)
    df["predicted_signal"] = np.tanh(df["sentiment_score"] * 0.5 + (df["close"].pct_change(10).fillna(0)) * 2.0)
    df["strategy_return"] = df["predicted_signal"].shift(1) * df["close"].pct_change()
    return df.fillna(0.0)


def test_factor_analyzer(sample_market_df):
    fa = FactorAnalyzer(sample_market_df)
    df_factors = fa.compute_factors()
    assert "factor_momentum_1m" in df_factors.columns
    assert "factor_sentiment" in df_factors.columns

    ic_res = fa.compute_ic(signal_col="predicted_signal", return_col="forward_return")
    assert "mean_ic" in ic_res
    assert "icir" in ic_res

    q_res = fa.compute_quantile_returns(signal_col="predicted_signal", quantiles=5)
    assert "quantile_returns" in q_res
    assert "long_short_spread" in q_res

    neut_series = fa.neutralize_factor("factor_sentiment", ["factor_volatility_20d"])
    assert len(neut_series) == len(sample_market_df)


def test_model_explainer():
    mock_fi = {
        "factor_momentum_1m": 0.40,
        "factor_sentiment": 0.30,
        "factor_volatility_20d": 0.20,
        "pe_ratio": 0.10,
    }
    explainer = ModelExplainer(model=None, feature_names=list(mock_fi.keys()))
    modality = explainer.compute_modality_attribution(mock_fi)
    assert "Market" in modality
    assert "News" in modality
    assert "Fundamentals" in modality
    assert pytest.approx(sum(modality.values()), 0.01) == 1.0


def test_robustness_tester(sample_market_df):
    def dummy_bt(p):
        cost = p.get("transaction_cost_bps", 10.0)
        return {"sharpe": 1.5 - cost / 100.0, "cagr": 0.15, "max_drawdown": -0.10}

    tester = RobustnessTester(dummy_bt)
    cost_df = tester.test_cost_sensitivity([0.0, 10.0, 50.0])
    assert len(cost_df) == 3

    slip_df = tester.test_slippage_sensitivity([0.0, 5.0])
    assert len(slip_df) == 2

    train_df, test_df = RobustnessTester.purged_train_test_split(sample_market_df, train_pct=0.7, purge_window=5, embargo_window=5)
    assert len(train_df) + len(test_df) <= len(sample_market_df)


def test_stress_tester(sample_market_df):
    st = StressTester(sample_market_df["strategy_return"])
    hist_res = st.run_historical_scenarios()
    assert "2020 COVID Crash" in hist_res

    shocks = st.run_hypothetical_shocks([-0.05, -0.10])
    assert "Shock -5%" in shocks

    liq = st.run_liquidity_stress()
    assert "stressed_sharpe_ratio" in liq


def test_uncertainty_analyzer(sample_market_df):
    df_preds = sample_market_df.copy()
    df_preds["model_xgb"] = df_preds["predicted_signal"] + 0.01
    df_preds["model_lstm"] = df_preds["predicted_signal"] - 0.01

    ua = UncertaintyAnalyzer(df_preds)
    df_unc = ua.compute_ensemble_uncertainty(["model_xgb", "model_lstm"])
    assert "disagreement_index" in df_unc.columns
    assert "ci_lower_95" in df_unc.columns

    df_preds["predicted_prob"] = (df_preds["predicted_signal"] + 1) / 2.0
    df_preds["realized_direction"] = (df_preds["forward_return"] > 0).astype(float)
    ua2 = UncertaintyAnalyzer(df_preds)
    cal_df = ua2.compute_reliability_calibration("predicted_prob", "realized_direction")
    assert not cal_df.empty


def test_error_analyzer(sample_market_df):
    df = sample_market_df.assign(predicted_return=sample_market_df["predicted_signal"]*0.02, realized_return=sample_market_df["forward_return"])
    ea = ErrorAnalyzer(df)
    metrics = ea.compute_error_metrics()
    assert "mae" in metrics
    assert "directional_accuracy" in metrics

    psi = ErrorAnalyzer.compute_psi(np.random.normal(0, 1, 100), np.random.normal(0.1, 1, 100))
    assert psi >= 0.0


def test_portfolio_attributor():
    trades_df = pd.DataFrame([
        {"ticker": "AAPL", "gross_return": 0.05, "cost_bps": 10.0, "slippage_bps": 5.0, "traded_value": 10000.0},
        {"ticker": "NVDA", "gross_return": 0.08, "cost_bps": 10.0, "slippage_bps": 5.0, "traded_value": 15000.0},
    ])
    att = PortfolioAttributor(trades_df)
    pnl_res = att.compute_pnl_decomposition()
    assert "total_gross_return" in pnl_res
    assert "transaction_cost_drag" in pnl_res

    asset_res = att.compute_asset_attribution()
    assert not asset_res.empty


def test_statistical_tester(sample_market_df):
    st = StatisticalTester(sample_market_df["strategy_return"])
    sig_res = st.test_performance_significance()
    assert "p_val_vs_zero" in sig_res

    boot_res = st.bootstrap_metrics(num_iterations=100)
    assert "sharpe" in boot_res
    assert "ci_lower" in boot_res["sharpe"]


def test_research_runner():
    config = {
        "experiment_id": "test_exp_runner",
        "ticker": "AAPL",
        "quantiles": 5,
    }
    runner = ResearchRunner(config)
    res = runner.run_experiment(demo=True)
    assert res["experiment_id"] == "test_exp_runner"
    assert "ic_analysis" in res
