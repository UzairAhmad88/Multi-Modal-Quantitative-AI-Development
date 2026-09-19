"""
REST API Routes for End-to-End Quantitative Research Pipeline Orchestrator OS.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from orchestration.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/pipeline", tags=["Pipeline Orchestrator OS"])
service = OrchestrationService()


class PipelineRunApiRequest(BaseModel):
    experiment_id: str = Field(default="EXP-END2END-001")
    symbols: List[str] = Field(default=["AAPL", "MSFT"])
    config: Optional[Dict[str, Any]] = Field(default=None)


@router.get("/health", summary="Get Pipeline Orchestrator Health")
def get_pipeline_health():
    return {
        "status": "healthy",
        "engine": "End-to-End Quantitative Research Pipeline Orchestrator OS",
        "stages": 14,
        "version": "1.0.0",
    }


@router.post("/run", summary="Trigger Full 14-Stage Pipeline Run")
def trigger_pipeline_run(request: PipelineRunApiRequest):
    run_state = service.run_pipeline(
        experiment_id=request.experiment_id,
        symbols=request.symbols,
        config=request.config,
    )
    return run_state.model_dump()


@router.get("/runs", summary="List Pipeline Runs")
def list_pipeline_runs():
    return service.list_pipeline_runs()


@router.get("/{run_id}", summary="Get Pipeline Run Details")
def get_pipeline_run(run_id: str):
    res = service.get_run_status(run_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Pipeline run '{run_id}' not found.")
    return res


@router.post("/{run_id}/resume", summary="Resume Failed or Paused Pipeline Run")
def resume_pipeline_run(run_id: str):
    res = service.resume_pipeline(run_id)
    return res.model_dump()
