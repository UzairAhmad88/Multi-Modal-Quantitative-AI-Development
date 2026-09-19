"""
REST API Endpoints for Phase 25 Portfolio Construction & Optimization Engine OS.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from portfolio.services.portfolio_service import PortfolioService
from portfolio.schemas.portfolio_schema import PortfolioConstraintsSchema
from portfolio.reports.generator import PortfolioReportGenerator
from portfolio.constraints.engine import ConstraintEngine
from portfolio.risk.attribution import PortfolioRiskAttribution

router = APIRouter(prefix="/portfolio-v2", tags=["Portfolio Construction OS (Phase 25)"])
service = PortfolioService()


class CreatePortfolioRequest(BaseModel):
    name: str = Field("Institutional Multi-Asset Portfolio", json_schema_extra={"example": "Institutional Multi-Asset Portfolio"})
    assets: List[str] = Field(["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"], json_schema_extra={"example": ["AAPL", "MSFT", "GOOGL"]})
    base_currency: str = Field("USD", json_schema_extra={"example": "USD"})
    initial_value: float = Field(100000.0, json_schema_extra={"example": 100000.0})
    constraints: Optional[PortfolioConstraintsSchema] = Field(default_factory=PortfolioConstraintsSchema)


class OptimizePortfolioRequest(BaseModel):
    portfolio_id: str = Field("PORT-001", json_schema_extra={"example": "PORT-001"})
    method: str = Field("mean_variance", json_schema_extra={"example": "mean_variance"})
    alpha_scores: Optional[Dict[str, float]] = Field(None, json_schema_extra={"example": {"AAPL": 0.05, "MSFT": 0.03}})
    cov_matrix: Optional[List[List[float]]] = Field(None)
    constraints_override: Optional[Dict[str, Any]] = Field(None)


class RebalancePortfolioRequest(BaseModel):
    portfolio_id: str = Field("PORT-001", json_schema_extra={"example": "PORT-001"})
    target_weights: Dict[str, float] = Field(..., json_schema_extra={"example": {"AAPL": 0.5, "MSFT": 0.5}})
    force: bool = Field(False)


@router.get("/health")
def portfolio_health():
    return {
        "status": "HEALTHY",
        "module": "Portfolio Construction OS",
        "phase": 25,
        "engine": "Active",
    }


@router.post("/create")
def create_portfolio(req: CreatePortfolioRequest):
    constraints_dict = req.constraints.model_dump() if req.constraints else {}
    port = service.create_portfolio(
        name=req.name,
        assets=req.assets,
        base_currency=req.base_currency,
        initial_value=req.initial_value,
        constraints=constraints_dict,
    )
    return port.to_dict()


@router.get("/{portfolio_id}")
def get_portfolio(portfolio_id: str):
    port = service.get_portfolio(portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")
    return port.to_dict()


@router.post("/optimize")
def optimize_portfolio(req: OptimizePortfolioRequest):
    result = service.optimize_portfolio(
        portfolio_id=req.portfolio_id,
        method=req.method,
        alpha_scores=req.alpha_scores,
        cov_matrix=req.cov_matrix,
        constraints_override=req.constraints_override,
    )
    return result


@router.post("/validate")
def validate_portfolio(portfolio_id: str, target_weights: Dict[str, float]):
    port = service.get_portfolio(portfolio_id)
    constraints = port.constraints if port else {}
    engine = ConstraintEngine(constraints)
    eval_res = engine.evaluate_all(target_weights, port.weights if port else None)
    return eval_res


@router.get("/{portfolio_id}/risk")
def get_portfolio_risk(portfolio_id: str):
    port = service.get_portfolio(portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")

    import numpy as np
    n = len(port.assets)
    cov = np.eye(n) * 0.04
    attr = PortfolioRiskAttribution.compute_full_attribution(port.weights, cov)
    return attr


@router.get("/{portfolio_id}/exposure")
def get_portfolio_exposure(portfolio_id: str):
    port = service.get_portfolio(portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")
    return {
        "portfolio_id": portfolio_id,
        "gross_exposure": port.gross_exposure,
        "net_exposure": port.net_exposure,
        "cash_weight": port.cash_weight,
        "leverage": port.leverage,
    }


@router.get("/{portfolio_id}/positions")
def get_portfolio_positions(portfolio_id: str):
    port = service.get_portfolio(portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")
    return {sym: pos.to_dict() for sym, pos in port.positions.items()}


@router.get("/{portfolio_id}/history")
def get_portfolio_history(portfolio_id: str):
    port = service.get_portfolio(portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")
    snapshot = port.create_snapshot()
    return {"portfolio_id": portfolio_id, "snapshots": [snapshot.to_dict()]}


@router.post("/{portfolio_id}/rebalance")
def rebalance_portfolio(portfolio_id: str, req: RebalancePortfolioRequest):
    event = service.rebalance_portfolio(
        portfolio_id=portfolio_id,
        target_weights=req.target_weights,
        force=req.force,
    )
    return event.to_dict()


@router.get("/{portfolio_id}/constraints")
def get_portfolio_constraints(portfolio_id: str):
    port = service.get_portfolio(portfolio_id)
    if not port:
        raise HTTPException(status_code=404, detail=f"Portfolio '{portfolio_id}' not found")
    return {"portfolio_id": portfolio_id, "constraints": port.constraints}


@router.get("/{portfolio_id}/report")
def get_portfolio_report(portfolio_id: str, method: str = "mean_variance"):
    opt_res = service.optimize_portfolio(portfolio_id=portfolio_id, method=method)
    report_md = PortfolioReportGenerator.generate_report_md(opt_res)
    return {"portfolio_id": portfolio_id, "report_markdown": report_md}
