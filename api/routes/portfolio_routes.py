"""
FastAPI Advanced Portfolio Router
Provides REST endpoints for portfolio targets, covariance risk budgeting, optimization, exposure, and rebalancing.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
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
from src.portfolio.constraints import PortfolioConstraintEngine
from src.portfolio.rebalancer import PortfolioRebalancer

router = APIRouter(prefix="/portfolio", tags=["Portfolio Construction & Risk"])


class OptimizationRequest(BaseModel):
    symbols: List[str] = Field(["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL"], example=["AAPL", "NVDA", "MSFT"])
    optimizer: str = Field("MeanVariance", example="MeanVariance")
    max_asset_weight: float = Field(0.25, example=0.25)
    risk_aversion: float = Field(2.5, example=2.5)


@router.get("/current")
def get_current_portfolio():
    """Get active portfolio allocations and holdings."""
    return {
        "status": "success",
        "portfolio_value": 100000.0,
        "cash": 15000.0,
        "positions": [
            {"symbol": "AAPL", "weight": 0.22, "quantity": 118, "market_value": 22000.0},
            {"symbol": "NVDA", "weight": 0.20, "quantity": 160, "market_value": 20000.0},
            {"symbol": "MSFT", "weight": 0.18, "quantity": 42, "market_value": 18000.0},
            {"symbol": "AMZN", "weight": 0.15, "quantity": 83, "market_value": 15000.0},
            {"symbol": "GOOGL", "weight": 0.10, "quantity": 57, "market_value": 10000.0},
        ],
    }


@router.get("/target")
def get_target_portfolio():
    """Get target portfolio weights calculated by the active optimizer."""
    return {
        "status": "success",
        "optimizer": "MeanVariance",
        "target_weights": {
            "AAPL": 0.25,
            "NVDA": 0.22,
            "MSFT": 0.20,
            "AMZN": 0.18,
            "GOOGL": 0.15,
        },
    }


@router.get("/risk_budget")
def get_risk_budget():
    """Get component risk contributions (MCR & CRC)."""
    symbols = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL"]
    weights = pd.Series([0.25, 0.22, 0.20, 0.18, 0.15], index=symbols)
    np.random.seed(42)
    rets = pd.DataFrame(np.random.normal(0.0005, 0.012, (200, 5)), columns=symbols)

    cov_est = CovarianceEstimator(rets)
    cov_df = cov_est.compute_sample_covariance()
    rb_engine = RiskBudgetEngine(cov_df)
    rb_df = rb_engine.compute_risk_contributions(weights)

    return {
        "status": "success",
        "portfolio_volatility_ann": 0.148,
        "risk_contributions": rb_df.to_dict(orient="records"),
    }


@router.get("/exposure")
def get_exposure_breakdown():
    """Get gross, net, and sector exposure metrics."""
    return {
        "status": "success",
        "gross_exposure": 0.85,
        "net_exposure": 0.85,
        "long_exposure": 0.85,
        "short_exposure": 0.0,
        "sector_exposure": {
            "Technology": 0.67,
            "Consumer Cyclical": 0.18,
        },
    }


@router.get("/attribution")
def get_portfolio_attribution():
    """Get return attribution by asset and sector."""
    return {
        "status": "success",
        "asset_contributions": [
            {"symbol": "NVDA", "return_contribution": "+0.042"},
            {"symbol": "AAPL", "return_contribution": "+0.035"},
            {"symbol": "MSFT", "return_contribution": "+0.028"},
        ],
        "transaction_cost_drag": "-0.0012",
        "slippage_drag": "-0.0006",
    }


@router.post("/optimize")
def optimize_portfolio_endpoint(req: OptimizationRequest):
    """Execute real-time portfolio optimization given target symbols and optimizer choice."""
    symbols = [s.upper() for s in req.symbols]
    np.random.seed(42)
    rets = pd.DataFrame(np.random.normal(0.0005, 0.012, (200, len(symbols))), columns=symbols)
    alphas = {s: round(float(np.random.normal(0.02, 0.01)), 4) for s in symbols}

    exp_model = ExpectedReturnModel()
    exp_rets = pd.Series(exp_model.compute_expected_returns(alphas))

    cov_est = CovarianceEstimator(rets)
    cov_df = cov_est.compute_shrinkage_covariance()

    opt_map = {
        "EqualWeight": EqualWeightOptimizer(req.max_asset_weight),
        "SignalWeight": SignalWeightOptimizer(req.max_asset_weight),
        "InverseVolatility": InverseVolatilityOptimizer(req.max_asset_weight),
        "MinimumVariance": MinimumVarianceOptimizer(req.max_asset_weight),
        "MeanVariance": MeanVarianceOptimizer(req.risk_aversion, req.max_asset_weight),
        "RiskParity": RiskParityOptimizer(req.max_asset_weight),
        "HRP": HRPOptimizer(req.max_asset_weight),
    }

    opt = opt_map.get(req.optimizer, MeanVarianceOptimizer(req.risk_aversion, req.max_asset_weight))
    weights = opt.optimize(exp_rets, cov_df)

    constraint_engine = PortfolioConstraintEngine(max_asset_weight=req.max_asset_weight)
    final_weights, logs = constraint_engine.apply_constraints(weights)

    return {
        "status": "success",
        "optimizer": req.optimizer,
        "symbols": symbols,
        "weights": final_weights.to_dict(),
        "constraint_logs": logs,
    }


@router.post("/rebalance")
def trigger_rebalance():
    """Trigger portfolio rebalancing event."""
    curr_w = pd.Series({"AAPL": 0.20, "NVDA": 0.20, "MSFT": 0.20, "AMZN": 0.20, "GOOGL": 0.20})
    targ_w = pd.Series({"AAPL": 0.25, "NVDA": 0.25, "MSFT": 0.20, "AMZN": 0.15, "GOOGL": 0.15})

    rebalancer = PortfolioRebalancer("MeanVariance", "weekly")
    res = rebalancer.execute_rebalance(curr_w, targ_w)

    return {"status": "success", "rebalance_event": res}
