"""
REST API Routes for Phase 22 Automated Quant Research Orchestrator.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from orchestrator.core.orchestrator import ResearchOrchestrator
from orchestrator.planner.experiment_planner import ExperimentPlanner, ResearchPlan
from orchestrator.campaigns.campaign_manager import CampaignManager
from orchestrator.monitoring.workflow_monitor import WorkflowMonitor

router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])

orchestrator = ResearchOrchestrator()
campaign_manager = CampaignManager()


class CreateWorkflowRequest(BaseModel):
    name: str = "Multimodal Quant Research Workflow"
    template: str = "full_research"
    configuration: Dict[str, Any] = Field(default_factory=dict)


class CreatePlanRequest(BaseModel):
    name: str = "Multimodal Research Plan"
    objective: str = "Evaluate market + news + fundamentals predictive performance"
    hypothesis: str = "Adding multi-modal features improves out-of-sample Sharpe ratio"
    dataset_id: str = "DS-SP500_DAILY-v1.0.0"
    models: List[str] = Field(default_factory=lambda: ["xgboost", "lstm", "transformer"])
    modalities: List[str] = Field(default_factory=lambda: ["market", "market_news", "all"])
    max_experiments: int = 20


class CreateCampaignRequest(BaseModel):
    name: str = "Multimodal Alpha Research Campaign"
    objective: str = "Automated research matrix over model architectures and modalities"
    plan: CreatePlanRequest


@router.post("/workflows")
def create_workflow(req: CreateWorkflowRequest):
    wf = orchestrator.create_workflow(
        name=req.name,
        template=req.template,
        custom_config=req.configuration,
    )
    return wf.dict()


@router.get("/workflows")
def list_workflows():
    return orchestrator.list_workflows()


@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str):
    wf = orchestrator.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf.dict()


@router.post("/workflows/{workflow_id}/validate")
def validate_workflow(workflow_id: str):
    try:
        results = orchestrator.validate_workflow(workflow_id)
        return {"workflow_id": workflow_id, "results": [r.dict() for r in results]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workflows/{workflow_id}/start")
def start_workflow(workflow_id: str):
    try:
        wf = orchestrator.start_workflow(workflow_id)
        return wf.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/pause")
def pause_workflow(workflow_id: str):
    try:
        wf = orchestrator.pause_workflow(workflow_id)
        return wf.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workflows/{workflow_id}/resume")
def resume_workflow(workflow_id: str):
    try:
        wf = orchestrator.resume_workflow(workflow_id)
        return wf.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workflows/{workflow_id}/cancel")
def cancel_workflow(workflow_id: str):
    try:
        wf = orchestrator.cancel_workflow(workflow_id)
        return wf.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workflows/{workflow_id}/retry")
def retry_workflow(workflow_id: str):
    try:
        wf = orchestrator.retry_workflow(workflow_id)
        return wf.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/workflows/{workflow_id}/status")
def get_workflow_status(workflow_id: str):
    wf = orchestrator.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    progress = WorkflowMonitor.get_progress(wf)
    return {"workflow_id": workflow_id, "status": wf.status.value, "progress": progress}


@router.get("/workflows/{workflow_id}/events")
def get_workflow_events(workflow_id: str):
    events = orchestrator.get_events(workflow_id)
    return {"workflow_id": workflow_id, "events_count": len(events), "events": events}


@router.post("/experiments/generate")
def generate_experiments_matrix(req: CreatePlanRequest):
    from dataclasses import asdict
    plan = ResearchPlan(
        plan_id=f"PLAN-{req.name.upper()[:6]}",
        name=req.name,
        objective=req.objective,
        hypothesis=req.hypothesis,
        dataset_id=req.dataset_id,
        models=req.models,
        modalities=req.modalities,
    )
    plan.resource_budget.max_experiments = req.max_experiments
    experiments = ExperimentPlanner.generate_matrix(plan)
    return {"experiments_count": len(experiments), "experiments": [asdict(e) for e in experiments]}


@router.post("/campaigns")
def create_campaign(req: CreateCampaignRequest):
    plan = ResearchPlan(
        plan_id=f"PLAN-{req.plan.name.upper()[:6]}",
        name=req.plan.name,
        objective=req.plan.objective,
        hypothesis=req.plan.hypothesis,
        dataset_id=req.plan.dataset_id,
        models=req.plan.models,
        modalities=req.plan.modalities,
    )
    campaign = campaign_manager.create_campaign(name=req.name, objective=req.objective, plan=plan)
    return campaign.to_dict()


@router.get("/campaigns")
def list_campaigns():
    return campaign_manager.list_campaigns()


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str):
    c = campaign_manager.get_campaign(campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return c.to_dict()


@router.get("/campaigns/{campaign_id}/report")
def get_campaign_report(campaign_id: str):
    try:
        report_md = campaign_manager.build_campaign_report(campaign_id)
        return {"campaign_id": campaign_id, "report_markdown": report_md}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/health")
def orchestrator_health():
    return orchestrator.get_health()
