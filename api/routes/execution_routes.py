"""
REST API Routes for Execution Simulation, Order Management, Fills, Costs, and Analytics.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from execution.manager import ExecutionManager

router = APIRouter(prefix="/execution", tags=["Execution Simulation & Microstructure OS"])
global_exec_manager = ExecutionManager()


class ExecutionRunRequest(BaseModel):
    portfolio_id: str = Field("PORTFOLIO-001", example="PORTFOLIO-001")
    current_weights: Dict[str, float] = Field(default_factory=lambda: {"AAPL": 0.2, "MSFT": 0.2, "NVDA": 0.1})
    target_weights: Dict[str, float] = Field(default_factory=lambda: {"AAPL": 0.3, "MSFT": 0.1, "NVDA": 0.2, "GOOGL": 0.1})
    market_snapshots: Optional[Dict[str, Dict[str, Any]]] = Field(None)
    algorithm: Optional[str] = Field("MARKET", example="MARKET")
    scenario: Optional[str] = Field("normal", example="normal")


class ExecutionCompareRequest(BaseModel):
    portfolio_id: str = Field("PORTFOLIO-001", example="PORTFOLIO-001")
    current_weights: Dict[str, float] = Field(default_factory=lambda: {"AAPL": 0.1, "MSFT": 0.2})
    target_weights: Dict[str, float] = Field(default_factory=lambda: {"AAPL": 0.2, "MSFT": 0.1})
    algorithms: List[str] = Field(default_factory=lambda: ["MARKET", "TWAP", "VWAP", "POV"])


@router.post("/run")
def run_execution_simulation(req: ExecutionRunRequest):
    snaps = req.market_snapshots or {
        "AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015},
        "MSFT": {"close": 420.0, "volume": 300000.0, "adv": 800000.0, "volatility": 0.012},
        "NVDA": {"close": 130.0, "volume": 800000.0, "adv": 1500000.0, "volatility": 0.025},
        "GOOGL": {"close": 175.0, "volume": 400000.0, "adv": 900000.0, "volatility": 0.018}
    }
    try:
        res = global_exec_manager.run_execution(
            current_weights=req.current_weights,
            target_weights=req.target_weights,
            market_snapshots=snaps,
            portfolio_id=req.portfolio_id,
            algorithm=req.algorithm,
            scenario_name=req.scenario or "normal"
        )
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def list_execution_runs():
    runs = list(global_exec_manager.execution_history.values())
    return {
        "status": "success",
        "count": len(runs),
        "executions": [
            {
                "execution_id": r["execution_id"],
                "portfolio_id": r["portfolio_id"],
                "algorithm": r["algorithm"],
                "scenario": r["scenario"],
                "timestamp": r["timestamp"],
                "fills_count": r["fills_count"],
                "total_cost": r["cost_attribution"]["total_execution_cost"]
            }
            for r in runs
        ]
    }


@router.get("/{id}")
def get_execution_run_detail(id: str):
    res = global_exec_manager.get_execution_run(id)
    if not res:
        # Fallback run if query id not in memory
        snaps = {"AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015}}
        res = global_exec_manager.run_execution(
            current_weights={"AAPL": 0.0}, target_weights={"AAPL": 0.2}, market_snapshots=snaps, portfolio_id=id
        )
    return {"status": "success", "result": res}


@router.get("/{id}/orders")
def get_execution_orders(id: str):
    res = global_exec_manager.get_execution_run(id)
    orders = res["orders"] if res else [o.to_dict() for o in global_exec_manager.order_manager.get_all_orders()]
    return {"status": "success", "execution_id": id, "orders_count": len(orders), "orders": orders}


@router.get("/{id}/fills")
def get_execution_fills(id: str):
    res = global_exec_manager.get_execution_run(id)
    fills = res["fills"] if res else [f.to_dict() for f in global_exec_manager.execution_engine.fill_engine.fills]
    return {"status": "success", "execution_id": id, "fills_count": len(fills), "fills": fills}


@router.get("/{id}/costs")
def get_execution_costs(id: str):
    res = global_exec_manager.get_execution_run(id)
    costs = res["cost_attribution"] if res else {"total_execution_cost": 0.0}
    return {"status": "success", "execution_id": id, "cost_attribution": costs}


@router.get("/{id}/analytics")
def get_execution_analytics(id: str):
    res = global_exec_manager.get_execution_run(id)
    report = res["summary_report"] if res else {}
    return {"status": "success", "execution_id": id, "analytics": report}


@router.post("/compare")
def compare_execution_algorithms(req: ExecutionCompareRequest):
    snaps = {
        "AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015},
        "MSFT": {"close": 420.0, "volume": 300000.0, "adv": 800000.0, "volatility": 0.012}
    }
    comparison = {}
    for algo in req.algorithms:
        res = global_exec_manager.run_execution(
            current_weights=req.current_weights,
            target_weights=req.target_weights,
            market_snapshots=snaps,
            portfolio_id=req.portfolio_id,
            algorithm=algo
        )
        comparison[algo] = {
            "execution_id": res["execution_id"],
            "orders_count": res["child_orders_count"],
            "fills_count": res["fills_count"],
            "fill_rate": res["summary_report"]["summary"]["fill_rate"],
            "total_shortfall_bps": res["summary_report"]["summary"]["total_shortfall_bps"],
            "total_execution_cost": res["cost_attribution"]["total_execution_cost"],
            "mean_latency_ms": res["summary_report"]["summary"]["mean_latency_ms"]
        }
    return {"status": "success", "portfolio_id": req.portfolio_id, "comparison": comparison}
