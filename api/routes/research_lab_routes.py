"""
REST API Routes for Research Laboratory Experiment Management, Lineage, and Reproducibility.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from research_lab.manager import ExperimentManager

router = APIRouter(prefix="/research-lab", tags=["Research Laboratory OS"])
global_lab_manager = ExperimentManager()


class CreateExperimentRequest(BaseModel):
    name: str = Field("Multimodal Alpha Experiment", example="Multimodal Alpha Experiment")
    template_name: str = Field("multimodal", example="multimodal")
    random_seed: int = Field(42, example=42)
    hypothesis: Optional[Dict[str, str]] = Field(None)
    custom_config: Optional[Dict[str, Any]] = Field(None)


class CompareLabExperimentsRequest(BaseModel):
    experiment_ids: List[str] = Field(default_factory=lambda: ["EXP-001", "EXP-002"])


@router.post("/experiments")
def create_experiment_endpoint(req: CreateExperimentRequest):
    exp = global_lab_manager.create_experiment(
        name=req.name,
        template_name=req.template_name,
        hypothesis=req.hypothesis,
        custom_config=req.custom_config,
        random_seed=req.random_seed
    )
    return {"status": "success", "experiment": exp.to_dict()}


@router.get("/experiments")
def list_experiments():
    exps = list(global_lab_manager.experiments.values())
    return {
        "status": "success",
        "count": len(exps),
        "experiments": [e.to_dict() for e in exps]
    }


@router.get("/experiments/{id}")
def get_experiment_detail(id: str):
    res = global_lab_manager.experiment_results.get(id)
    if not res:
        res = global_lab_manager.run_experiment(id)
    return {"status": "success", "result": res}


@router.post("/experiments/{id}/run")
def run_experiment_endpoint(id: str):
    try:
        res = global_lab_manager.run_experiment(id)
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/{id}/clone")
def clone_experiment_endpoint(id: str, new_name: Optional[str] = Query(None)):
    cloned = global_lab_manager.clone_experiment(id, new_name=new_name)
    return {"status": "success", "cloned_experiment": cloned.to_dict()}


@router.post("/experiments/{id}/replicate")
def replicate_experiment_endpoint(id: str):
    res = global_lab_manager.replicate_experiment(id)
    return {"status": "success", "replication": res}


@router.get("/experiments/{id}/lineage")
def get_experiment_lineage(id: str):
    res = global_lab_manager.experiment_results.get(id)
    if not res:
        res = global_lab_manager.run_experiment(id)
    return {"status": "success", "lineage": res["lineage"]}


@router.get("/experiments/{id}/metrics")
def get_experiment_metrics(id: str):
    res = global_lab_manager.experiment_results.get(id)
    metrics = res["metrics"] if res else global_lab_manager.metric_store.get_run_metrics(id)
    return {"status": "success", "experiment_id": id, "metrics": metrics}


@router.get("/experiments/{id}/artifacts")
def get_experiment_artifacts(id: str):
    arts = [a for a in global_lab_manager.artifact_store.artifacts_index.values() if a["experiment_id"] == id]
    return {"status": "success", "experiment_id": id, "artifacts": arts}


@router.post("/compare")
def compare_lab_experiments(req: CompareLabExperimentsRequest):
    res = global_lab_manager.compare_experiments(req.experiment_ids)
    return {"status": "success", "comparison": res}


@router.get("/reports/{id}")
def get_lab_report(id: str, format: str = Query("markdown", enum=["markdown", "html", "json"])):
    res = global_lab_manager.experiment_results.get(id)
    if not res:
        res = global_lab_manager.run_experiment(id)
    reports = res["reports"]
    if format == "html":
        return Response(content=reports["html"], media_type="text/html")
    elif format == "json":
        return Response(content=reports["json"], media_type="application/json")
    return {"status": "success", "experiment_id": id, "markdown_report": reports["markdown"]}
