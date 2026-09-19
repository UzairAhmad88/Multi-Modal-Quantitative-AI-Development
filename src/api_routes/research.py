"""
FastAPI Research Engine Router
Provides REST API endpoints for factor analysis, model explainability, sensitivity testing,
stress testing, and statistical bootstrapping.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from src.research.factor_analysis import FactorAnalyzer
from src.research.explainability import ModelExplainer
from src.research.robustness import RobustnessTester
from src.research.stress_testing import StressTester
from src.research.statistical_tests import StatisticalTester

router = APIRouter(prefix="/research", tags=["Quantitative Research Lab"])


@router.get("/factors/{ticker}")
def get_factor_analysis(ticker: str, quantiles: int = Query(5, ge=2, le=10)):
    """Retrieve factor analysis, Information Coefficients (IC), and quantile returns."""
    try:
        dates = pd.date_range(start="2022-01-01", periods=200, freq="B")
        np.random.seed(42)
        price = 150.0 + np.cumsum(np.random.normal(0.1, 1.5, len(dates)))

        df = pd.DataFrame({
            "date": dates,
            "ticker": ticker.upper(),
            "close": price,
            "volume": np.random.randint(1000000, 5000000, len(dates)),
            "sentiment_score": np.random.normal(0.1, 0.4, len(dates)),
            "pe_ratio": 22.0 + np.random.normal(0, 0.5, len(dates)),
            "roe": 0.16 + np.random.normal(0, 0.01, len(dates)),
        })
        df["forward_return"] = df["close"].pct_change(5).shift(-5)
        df["predicted_signal"] = np.tanh(df["sentiment_score"] * 0.4 + (df["close"].pct_change(10).fillna(0)) * 1.5)

        analyzer = FactorAnalyzer(df)
        analyzer.compute_factors()
        ic_stats = analyzer.compute_ic(signal_col="predicted_signal", return_col="forward_return")
        ic_decay = analyzer.compute_ic_decay(signal_col="predicted_signal")
        quantiles_res = analyzer.compute_quantile_returns(signal_col="predicted_signal", quantiles=quantiles)

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "ic_analysis": ic_stats,
            "ic_decay": ic_decay,
            "quantile_spread": quantiles_res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explainability/{ticker}")
def get_model_explainability(ticker: str):
    """Retrieve SHAP feature importances and modality attributions."""
    try:
        mock_fi = {
            "factor_momentum_1m": 0.32,
            "factor_sentiment": 0.28,
            "factor_volatility_20d": 0.18,
            "factor_liquidity": 0.10,
            "factor_value": 0.07,
            "factor_quality": 0.05,
        }
        explainer = ModelExplainer(model=None, feature_names=list(mock_fi.keys()))
        modality_att = explainer.compute_modality_attribution(mock_fi)

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "feature_importance": mock_fi,
            "modality_attribution": modality_att,
            "top_features": [
                {"feature": "factor_momentum_1m", "impact": "+0.32", "modality": "Market"},
                {"feature": "factor_sentiment", "impact": "+0.28", "modality": "News"},
                {"feature": "factor_volatility_20d", "impact": "-0.18", "modality": "Market"},
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stress_test/{ticker}")
def get_stress_tests(ticker: str):
    """Retrieve historical crisis simulations and hypothetical market shock metrics."""
    try:
        np.random.seed(42)
        rets = pd.Series(np.random.normal(0.0008, 0.012, 500))
        tester = StressTester(rets)

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "historical_scenarios": tester.run_historical_scenarios(),
            "hypothetical_shocks": tester.run_hypothetical_shocks(),
            "liquidity_stress": tester.run_liquidity_stress(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bootstrap/{ticker}")
def get_bootstrap_confidence(ticker: str):
    """Retrieve non-parametric 95% bootstrap confidence intervals for Sharpe, CAGR, and Drawdown."""
    try:
        np.random.seed(42)
        rets = pd.Series(np.random.normal(0.0009, 0.011, 250))
        stat_tester = StatisticalTester(rets)
        ci_res = stat_tester.bootstrap_metrics(num_iterations=500)
        sig_tests = stat_tester.test_performance_significance()

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "significance_tests": sig_tests,
            "bootstrap_intervals": ci_res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
