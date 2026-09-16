"""
REST API Endpoints for Phase 26 Advanced Quantitative Risk & Stress Testing OS.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from risk.services.risk_service import RiskService
from risk.schemas.risk_schema import StressScenarioRequest, MonteCarloRequest
from risk.reports.generator import RiskReportGenerator

router = APIRouter(prefix="/risk-v2", tags=["Advanced Risk OS (Phase 26)"])
service = RiskService()


class RunRiskAnalysisRequest(BaseModel):
    portfolio_id: str = Field("PORT-001", json_schema_extra={"example": "PORT-001"})
    weights: Optional[Dict[str, float]] = Field(None, json_schema_extra={"example": {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3}})
    returns_history: Optional[List[List[float]]] = Field(None)
    cov_matrix: Optional[List[List[float]]] = Field(None)
    portfolio_value: float = Field(100000.0, json_schema_extra={"example": 100000.0})


@router.get("/health")
def risk_health():
    return {
        "status": "HEALTHY",
        "module": "Advanced Quantitative Risk & Stress Testing OS",
        "phase": 26,
        "engine": "Active",
    }


@router.post("/run")
def run_risk_analysis(req: RunRiskAnalysisRequest):
    res = service.run_risk_analysis(
        portfolio_id=req.portfolio_id,
        weights=req.weights,
        returns_history=req.returns_history,
        cov_matrix=req.cov_matrix,
        portfolio_value=req.portfolio_value,
    )
    return res


@router.get("/{risk_id}")
def get_risk_analysis(risk_id: str):
    import os, json
    filepath = os.path.join(service.storage_dir, f"{risk_id}.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Risk analysis '{risk_id}' not found")
    with open(filepath, "r") as f:
        return json.load(f)


@router.get("/{risk_id}/metrics")
def get_risk_metrics(risk_id: str):
    data = get_risk_analysis(risk_id)
    return {
        "risk_id": risk_id,
        "volatility": data.get("market_risk", {}).get("historical_volatility"),
        "beta": data.get("market_risk", {}).get("beta"),
        "var_95": data.get("tail_risk", {}).get("var_95_historical"),
        "cvar_95": data.get("tail_risk", {}).get("cvar_95"),
        "max_drawdown": data.get("drawdown_analysis", {}).get("max_drawdown"),
    }


@router.get("/{risk_id}/var")
def get_var_metrics(risk_id: str):
    data = get_risk_analysis(risk_id)
    return {"risk_id": risk_id, "tail_risk": data.get("tail_risk", {})}


@router.get("/{risk_id}/cvar")
def get_cvar_metrics(risk_id: str):
    data = get_risk_analysis(risk_id)
    return {"risk_id": risk_id, "cvar_95": data.get("tail_risk", {}).get("cvar_95")}


@router.get("/{risk_id}/drawdown")
def get_drawdown_analysis(risk_id: str):
    data = get_risk_analysis(risk_id)
    return {"risk_id": risk_id, "drawdown_analysis": data.get("drawdown_analysis", {})}


@router.get("/{risk_id}/contributions")
def get_risk_contributions(risk_id: str):
    data = get_risk_analysis(risk_id)
    return {"risk_id": risk_id, "contributions": data.get("portfolio_risk", {}).get("contributions", {})}


@router.post("/{risk_id}/stress")
def run_stress_test(risk_id: str, req: StressScenarioRequest):
    data = get_risk_analysis(risk_id)
    pid = data.get("portfolio_id", "PORT-001")
    weights = data.get("portfolio_risk", {}).get("exposures", {})
    w = {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3}

    res = service.engine.stress_engine.run_scenario(
        scenario_id=req.scenario_id,
        portfolio_id=pid,
        weights=w,
    )
    return res.to_dict()


@router.post("/{risk_id}/monte-carlo")
def run_monte_carlo(risk_id: str, req: MonteCarloRequest):
    data = get_risk_analysis(risk_id)
    pid = data.get("portfolio_id", "PORT-001")
    w = {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3}
    import numpy as np
    cov = np.eye(3) * 0.04

    res = service.engine.mc_engine.run_simulation(
        portfolio_id=pid,
        weights=w,
        cov_matrix=cov,
        num_simulations=req.simulations,
        horizon_days=req.horizon,
        random_seed=req.random_seed,
    )
    return res


@router.get("/{risk_id}/limits")
def get_risk_limits(risk_id: str):
    data = get_risk_analysis(risk_id)
    return {"risk_id": risk_id, "limits_status": data.get("risk_limits_status", {})}


@router.get("/{risk_id}/report")
def get_risk_report(risk_id: str):
    data = get_risk_analysis(risk_id)
    report_md = RiskReportGenerator.generate_report_md(data)
    return {"risk_id": risk_id, "report_markdown": report_md}
