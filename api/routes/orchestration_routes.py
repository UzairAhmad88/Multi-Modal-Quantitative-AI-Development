"""
API Router for Phase 14 Automated Research Pipeline & Orchestration.
Exposes endpoints for running, listing, resuming, cancelling, comparing, and reproducing research experiments.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from research.registry.registry import ExperimentRegistry
from orchestration.pipeline import ResearchPipeline
from orchestration.logging_manager import LoggingManager

router = APIRouter(prefix="/research", tags=["Research Orchestration"])
registry = ExperimentRegistry()


class CreateExperimentRequest(BaseModel):
    name: str = Field(..., example="multimodal_baseline")
    config: Dict[str, Any] = Field(..., example={"experiment": {"name": "baseline"}, "data": {"symbols": ["AAPL"]}})
    tags: Optional[List[str]] = Field(default=[], example=["multimodal", "baseline"])
    notes: Optional[str] = Field(default="", example="Baseline multimodal experiment")


class CompareRequest(BaseModel):
    id1: str = Field(..., example="RUN-20260916-0001")
    id2: str = Field(..., example="RUN-20260916-0002")


class ReproduceRequest(BaseModel):
    run_id: str = Field(..., example="RUN-20260916-0001")


def _run_pipeline_task(config: Dict[str, Any], resume_run_id: Optional[str] = None):
    pipeline = ResearchPipeline(config=config, resume_run_id=resume_run_id)
    pipeline.execute()


@router.get("/experiments", response_model=Dict[str, Any])

def list_experiments(
    model: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    dataset: Optional[str] = Query(None),
    name: Optional[str] = Query(None)
):
    runs = registry.list_experiments(model=model, symbol=symbol, status=status, dataset=dataset, name=name)
    return {
        "status": "success",
        "count": len(runs),
        "experiments": runs
    }


@router.post("/experiments", response_model=Dict[str, Any])
def create_experiment(req: CreateExperimentRequest):
    exp_id = f"EXP-{ResearchPipeline._generate_timestamp_id()}"
    registry.register_experiment(
        experiment_id=exp_id,
        name=req.name,
        config=req.config,
        tags=req.tags,
        notes=req.notes or ""
    )
    return {
        "status": "success",
        "experiment_id": exp_id,
        "message": f"Registered experiment '{req.name}' successfully."
    }


@router.get("/experiments/{id}", response_model=Dict[str, Any])
def get_experiment_details(id: str):
    if id.startswith("EXP-"):
        res = registry.get_experiment(id)
    else:
        res = registry.get_run(id)

    if not res:
        raise HTTPException(status_code=404, detail=f"Experiment or Run with ID '{id}' not found.")
    return {"status": "success", "data": res}


@router.post("/experiments/{id}/run", response_model=Dict[str, Any])
def trigger_experiment_run(id: str, background_tasks: BackgroundTasks):
    exp = registry.get_experiment(id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{id}' not found.")

    config = exp.get("config", {})
    pipeline = ResearchPipeline(config=config)

    # Launch execution asynchronously
    background_tasks.add_task(pipeline.execute)

    return {
        "status": "success",
        "experiment_id": exp.get("experiment_id"),
        "run_id": pipeline.run_id,
        "message": "Pipeline execution started in background."
    }


@router.post("/runs/{id}/resume", response_model=Dict[str, Any])
def resume_run(id: str, background_tasks: BackgroundTasks):
    run = registry.get_run(id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{id}' not found.")

    config = run.get("config", {})
    pipeline = ResearchPipeline(config=config, resume_run_id=id)

    background_tasks.add_task(pipeline.execute)

    return {
        "status": "success",
        "run_id": id,
        "message": f"Resuming run '{id}' from checkpoint in background."
    }


@router.post("/runs/{id}/cancel", response_model=Dict[str, Any])
def cancel_run(id: str):
    run = registry.get_run(id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{id}' not found.")

    registry.update_run_status(id, status="CANCELLED", error="Cancelled by user via API")
    return {
        "status": "success",
        "run_id": id,
        "message": f"Run '{id}' marked as CANCELLED."
    }


@router.get("/runs/{id}", response_model=Dict[str, Any])
def get_run_status(id: str):
    run = registry.get_run(id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{id}' not found.")
    return {"status": "success", "run": run}


@router.get("/runs/{id}/logs", response_model=Dict[str, Any])
def get_run_logs(id: str, limit: int = 100):
    lm = LoggingManager(run_id=id)
    logs = lm.read_logs(limit=limit)
    return {"status": "success", "run_id": id, "count": len(logs), "logs": logs}


@router.get("/runs/{id}/artifacts", response_model=Dict[str, Any])
def get_run_artifacts(id: str):
    run = registry.get_run(id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{id}' not found.")
    return {
        "status": "success",
        "run_id": id,
        "artifacts": run.get("artifacts", {})
    }


@router.post("/compare", response_model=Dict[str, Any])
def compare_experiments(req: CompareRequest):
    res = registry.compare_runs(req.id1, req.id2)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return {"status": "success", "comparison": res}


@router.post("/reproduce", response_model=Dict[str, Any])
def reproduce_experiment(req: ReproduceRequest, background_tasks: BackgroundTasks):
    run = registry.get_run(req.run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{req.run_id}' not found.")

    config = run.get("config", {})
    pipeline = ResearchPipeline(config=config)
    background_tasks.add_task(pipeline.execute)

    return {
        "status": "success",
        "original_run_id": req.run_id,
        "new_run_id": pipeline.run_id,
        "message": "Reproduction run initiated in background."
    }
