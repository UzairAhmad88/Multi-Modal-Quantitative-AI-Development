"""
REST API Routes for Portfolio Optimization Engine & Position Sizing.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from portfolio_optimization.manager import PortfolioOptimizationManager

router = APIRouter(prefix="/portfolio_opt", tags=["Portfolio Optimization System"])
mgr = PortfolioOptimizationManager()


class OptimizeRequest(BaseModel):
    signals: Dict[str, float] = Field({"AAPL": 0.75, "MSFT": 0.60, "NVDA": 0.85}, description="Alpha signals")
    method: str = Field("mean_variance", description="Optimization method: equal_weight, inverse_volatility, risk_parity, mean_variance, minimum_variance, target_volatility")
    risk_aversion: float = Field(2.0, description="Risk aversion coefficient")
    max_weight: float = Field(0.35, description="Maximum single asset weight")
    long_only: bool = Field(True, description="Long-only constraint")


class RebalanceRequest(BaseModel):
    portfolio_id: str = Field(..., description="Target Portfolio ID")
    current_weights: Dict[str, float] = Field({"AAPL": 0.20, "MSFT": 0.20, "NVDA": 0.20}, description="Current weights")
    prices: Dict[str, float] = Field({"AAPL": 180.0, "MSFT": 410.0, "NVDA": 120.0}, description="Current prices")
    portfolio_value: float = Field(100000.0, description="Total portfolio cash value")


@router.post("/optimize")
def optimize_portfolio_endpoint(req: OptimizeRequest) -> Dict[str, Any]:
    """Optimizes portfolio allocation given signals and constraints."""
    config = {
        "portfolio": {"method": req.method, "name": f"{req.method}_portfolio"},
        "objective": {"risk_aversion": req.risk_aversion},
        "constraints": {"long_only": req.long_only, "max_weight": req.max_weight}
    }
    res = mgr.optimize_portfolio(alpha_signals=req.signals, config=config)
    if res.get("status") == "FAILED":
        raise HTTPException(status_code=400, detail=res.get("reason", "Optimization failed"))
    return res


@router.get("/list")
def list_portfolios_endpoint() -> Dict[str, Any]:
    """Lists registered portfolio optimizations."""
    ports = mgr.list_portfolios()
    return {"portfolios": ports, "total": len(ports)}


@router.get("/{portfolio_id}")
def get_portfolio_endpoint(portfolio_id: str) -> Dict[str, Any]:
    """Gets specific portfolio optimization record."""
    port = mgr.get_portfolio(portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return port


@router.post("/rebalance")
def rebalance_portfolio_endpoint(req: RebalanceRequest) -> Dict[str, Any]:
    """Generates rebalance share orders for target portfolio."""
    port = mgr.get_portfolio(req.portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail="Target portfolio not found")
    from portfolio_optimization.portfolio.rebalancer import RebalancingEngine
    rebalancer = RebalancingEngine()
    orders = rebalancer.generate_rebalance_orders(req.current_weights, port["weights"], req.prices, portfolio_value=req.portfolio_value)
    return orders
