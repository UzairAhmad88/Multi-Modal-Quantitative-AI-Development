"""
REST API Routes for Strategy Research Evaluation, Out-Of-Sample Validation, and Research Reports.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from research_evaluation.manager import ResearchEvaluationManager

router = APIRouter(prefix="/research", tags=["Research Evaluation & Statistical Validation OS"])
global_eval_manager = ResearchEvaluationManager()


class StrategyEvaluateRequest(BaseModel):
    strategy_id: str = Field("STRATEGY-001", example="STRATEGY-001")
    returns: Optional[List[float]] = Field(None)
    market_returns: Optional[List[float]] = Field(None)
    signals: Optional[List[float]] = Field(None)


class WalkForwardRequest(BaseModel):
    strategy_id: str = Field("STRATEGY-001", example="STRATEGY-001")
    train_period: int = Field(756, example=756)
    test_period: int = Field(126, example=126)
    expanding: bool = Field(True, example=True)


class CompareStrategiesRequest(BaseModel):
    strategies: Dict[str, List[float]] = Field(
        default_factory=lambda: {
            "MultiModal_QuantNet": [0.001, 0.002, -0.0005, 0.0015, 0.003],
            "Equal_Weight_Baseline": [0.0005, 0.001, -0.001, 0.0008, 0.0012]
        }
    )


@router.post("/evaluate")
def run_strategy_evaluation(req: StrategyEvaluateRequest):
    try:
        res = global_eval_manager.evaluate_strategy(
            strategy_id=req.strategy_id,
            returns=req.returns,
            market_returns=req.market_returns,
            signals=req.signals
        )
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evaluations")
def list_evaluations():
    evals = list(global_eval_manager.evaluation_history.values())
    return {
        "status": "success",
        "count": len(evals),
        "evaluations": [
            {
                "evaluation_id": e["evaluation_id"],
                "strategy_id": e["strategy_id"],
                "timestamp": e["timestamp"],
                "cagr": e["performance"]["cagr"],
                "sharpe_ratio": e["performance"]["sharpe_ratio"],
                "robustness_score": e["robustness"]["robustness_score"]
            }
            for e in evals
        ]
    }


@router.get("/evaluations/{id}")
def get_evaluation_detail(id: str):
    res = global_eval_manager.get_evaluation(id)
    if not res:
        res = global_eval_manager.evaluate_strategy(strategy_id=id)
    return {"status": "success", "result": res}


@router.post("/walk-forward")
def run_walk_forward(req: WalkForwardRequest):
    res = global_eval_manager.evaluate_strategy(strategy_id=req.strategy_id)
    return {"status": "success", "strategy_id": req.strategy_id, "walk_forward": res["walk_forward"]}


@router.post("/robustness")
def run_robustness(req: StrategyEvaluateRequest):
    res = global_eval_manager.evaluate_strategy(strategy_id=req.strategy_id, returns=req.returns)
    return {"status": "success", "strategy_id": req.strategy_id, "robustness": res["robustness"]}


@router.post("/sensitivity")
def run_sensitivity(req: StrategyEvaluateRequest):
    res = global_eval_manager.evaluate_strategy(strategy_id=req.strategy_id, returns=req.returns)
    return {"status": "success", "strategy_id": req.strategy_id, "sensitivity": res["sensitivity"]}


@router.post("/compare")
def compare_strategies_endpoint(req: CompareStrategiesRequest):
    res = global_eval_manager.strat_comparator.compare_strategies(req.strategies)
    return {"status": "success", "comparison": res["strategy_comparison"]}


@router.get("/evaluations/{id}/report")
def get_evaluation_report(id: str, format: str = Query("markdown", enum=["markdown", "html"])):
    res = global_eval_manager.get_evaluation(id)
    if not res:
        res = global_eval_manager.evaluate_strategy(strategy_id=id)

    if format == "html":
        return Response(content=res["html_report"], media_type="text/html")
    return {"status": "success", "evaluation_id": id, "markdown_report": res["markdown_report"]}
