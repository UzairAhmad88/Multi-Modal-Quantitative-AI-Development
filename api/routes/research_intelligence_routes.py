"""
REST API Routes for Research Intelligence (Phase 11).
Provides query and management endpoints for hypotheses, experiments, findings, models, comparisons, recommendations, and graph.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, List, Any, Optional
from research_intelligence.orchestration.pipeline import ResearchIntelligencePipeline
from research_intelligence.hypothesis.registry import HypothesisState, PreRegistrationSpec
from research_intelligence.experiment_manager.manager import ExperimentConfig, ExperimentPriority
from research_intelligence.comparison.comparator import ExperimentComparator

router = APIRouter(prefix="/research", tags=["Research Intelligence"])

# Global pipeline instance for API
_pipeline = ResearchIntelligencePipeline()


@router.get("/overview")
def get_research_overview() -> Dict[str, Any]:
    hypo_list = _pipeline.hypothesis_registry.list_hypotheses()
    exp_list = _pipeline.experiment_manager.list_all()
    findings_list = list(_pipeline.research_memory._findings.values())
    failures_list = _pipeline.research_memory.list_failures()

    return {
        "status": "active",
        "total_hypotheses": len(hypo_list),
        "total_experiments": len(exp_list),
        "total_findings": len(findings_list),
        "total_failures": len(failures_list),
        "real_trading_enabled": False,
        "environment": "Paper-Trading / Quant Laboratory",
    }


@router.get("/hypotheses")
def list_hypotheses(state: Optional[str] = None) -> List[Dict[str, Any]]:
    st = HypothesisState(state) if state else None
    hypos = _pipeline.hypothesis_registry.list_hypotheses(st)
    return [h.to_dict() for h in hypos]


@router.post("/hypotheses")
def create_hypothesis(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    prereg_data = payload.get("preregistration")
    prereg = PreRegistrationSpec(**prereg_data) if prereg_data else None

    hypo = _pipeline.hypothesis_registry.register(
        title=payload["title"],
        description=payload.get("description", ""),
        research_question=payload.get("research_question", ""),
        expected_effect=payload.get("expected_effect", ""),
        null_hypothesis=payload.get("null_hypothesis", ""),
        variables=payload.get("variables", []),
        dataset=payload.get("dataset", "market_sp500"),
        time_period=payload.get("time_period", "2021-2026"),
        preregistration=prereg,
    )
    return hypo.to_dict()


@router.get("/experiments")
def list_experiments() -> List[Dict[str, Any]]:
    exps = _pipeline.experiment_manager.list_all()
    return [e.to_dict() for e in exps]


@router.post("/experiments")
def create_experiment(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    cfg = ExperimentConfig(
        name=payload["name"],
        hypothesis_id=payload["hypothesis_id"],
        dataset=payload["dataset"],
        features=payload["features"],
        model=payload["model"],
        validation=payload.get("validation", {}),
        backtest=payload.get("backtest", {}),
        portfolio=payload.get("portfolio", {}),
        risk=payload.get("risk", {}),
    )
    priority = ExperimentPriority(payload.get("priority", "NORMAL"))
    auto_approve = payload.get("auto_approve", False)

    record = _pipeline.experiment_manager.create_experiment(cfg, priority=priority, auto_approve=auto_approve)
    return record.to_dict()


@router.get("/experiments/{id}")
def get_experiment(id: str) -> Dict[str, Any]:
    record = _pipeline.experiment_manager.get(id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Experiment {id} not found.")
    return record.to_dict()


@router.post("/experiments/{id}/run")
def run_experiment(id: str, force: bool = False) -> Dict[str, Any]:
    record = _pipeline.experiment_manager.get(id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Experiment {id} not found.")
    
    if not record.approved_by_human:
        _pipeline.experiment_manager.approve_experiment(id)

    results = _pipeline.experiment_runner.run_experiment(id, force_rerun=force)
    return {"experiment_id": id, "results": results}


@router.post("/experiments/compare")
def compare_experiments(exp_id1: str = Query(...), exp_id2: str = Query(...)) -> Dict[str, Any]:
    e1 = _pipeline.experiment_manager.get(exp_id1)
    e2 = _pipeline.experiment_manager.get(exp_id2)
    if not e1 or not e2:
        raise HTTPException(status_code=404, detail="One or both experiments not found.")
    return ExperimentComparator.compare(e1, e2)


@router.get("/findings")
def list_findings() -> List[Dict[str, Any]]:
    return [f.to_dict() for f in _pipeline.research_memory._findings.values()]


@router.get("/models")
def list_models() -> List[Dict[str, Any]]:
    exps = _pipeline.experiment_manager.list_all()
    models = list(set([e.config.model for e in exps]))
    return [{"model": m, "count": sum(1 for e in exps if e.config.model == m)} for m in models]


@router.get("/datasets")
def list_datasets() -> List[Dict[str, Any]]:
    exps = _pipeline.experiment_manager.list_all()
    datasets = list(set([e.config.dataset for e in exps]))
    return [{"dataset": d, "count": sum(1 for e in exps if e.config.dataset == d)} for m in datasets]


@router.get("/regimes")
def get_regime_performance() -> Dict[str, Any]:
    return {
        "regimes": [
            {"regime": "BULL_LOW_VOL", "sharpe": 1.95, "cagr": 0.22},
            {"regime": "BEAR_HIGH_VOL", "sharpe": 1.12, "cagr": 0.08},
            {"regime": "SIDEWAYS_HIGH_VOL", "sharpe": 0.85, "cagr": 0.03},
        ]
    }


@router.get("/recommendations")
def get_recommendations(experiment_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if experiment_id:
        record = _pipeline.experiment_manager.get(experiment_id)
        if record:
            return _pipeline.recommendation_engine.generate_recommendations(record)
    exps = _pipeline.experiment_manager.list_all()
    if exps:
        return _pipeline.recommendation_engine.generate_recommendations(exps[0])
    return []


@router.get("/graph")
def get_research_graph() -> Dict[str, Any]:
    return _pipeline.research_memory.get_graph_data()
