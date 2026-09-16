"""
MLOps API Routes for Quant AI Platform
Endpoints for Experiment Manager, Model Registry, Dataset Registry, Feature Registry, and Lineage.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.mlops.experiments import ExperimentManager
from src.mlops.datasets import DatasetRegistry
from src.mlops.features import FeatureRegistry
from src.mlops.models import ModelRegistry
from src.mlops.strategies import StrategyRegistry
from src.mlops.lineage import LineageTracker
from src.mlops.metrics_store import MetricStore

router = APIRouter(prefix="/mlops", tags=["MLOps & Experiment Registry"])

exp_mgr = ExperimentManager()
ds_reg = DatasetRegistry()
feat_reg = FeatureRegistry()
model_reg = ModelRegistry()
strat_reg = StrategyRegistry()
lineage_tr = LineageTracker()
metric_st = MetricStore()


# Models API
@router.get("/models")
def list_models():
    return {"status": "success", "models": model_reg.list_models()}


@router.get("/models/{model_id}")
def get_model(model_id: str):
    model = model_reg.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"status": "success", "model": model}


class ModelRegisterRequest(BaseModel):
    model_name: str
    model_type: str
    version: str = "v1.0.0"
    framework: str = "PyTorch"
    feature_version: str = "v1.0.0"
    training_dataset: str = "sp500_daily"
    metrics: Dict[str, float] = Field(default_factory=dict)
    model_object: Optional[Any] = None


@router.post("/models/register")
def register_model(req: ModelRegisterRequest):
    entry = model_reg.register_model(
        model_name=req.model_name,
        model_type=req.model_type,
        version=req.version,
        framework=req.framework,
        feature_version=req.feature_version,
        training_dataset=req.training_dataset,
        metrics=req.metrics,
        model_object=req.model_object
    )
    return {"status": "success", "registered_model": entry}


@router.post("/models/{model_id}/validate")
def validate_model(model_id: str):
    try:
        updated = model_reg.update_status(model_id, "VALIDATED")
        return {"status": "success", "model": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/{model_id}/promote")
def promote_model(model_id: str, to_status: str = "PAPER"):
    try:
        updated = model_reg.update_status(model_id, to_status)
        return {"status": "success", "model": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/{model_id}/archive")
def archive_model(model_id: str):
    try:
        updated = model_reg.update_status(model_id, "ARCHIVED")
        return {"status": "success", "model": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Experiments API
@router.get("/experiments")
def list_experiments():
    return {"status": "success", "experiments": exp_mgr.list_experiments()}


@router.get("/experiments/{exp_id}")
def get_experiment(exp_id: str):
    exp = exp_mgr.get_experiment(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"status": "success", "experiment": exp}


class ExperimentCreateRequest(BaseModel):
    name: str
    description: str = ""
    config: Dict[str, Any] = Field(default_factory=dict)


@router.post("/experiments")
def create_experiment(req: ExperimentCreateRequest):
    exp = exp_mgr.create_experiment(name=req.name, description=req.description, config=req.config)
    return {"status": "success", "experiment": exp}


@router.get("/experiments/{exp_id}/metrics")
def get_experiment_metrics(exp_id: str):
    exp = exp_mgr.get_experiment(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    runs = exp.get("runs", [])
    metrics = {}
    for run in runs:
        run_metrics = metric_st.get_run_metrics(run.get("run_id"))
        if run_metrics:
            metrics[run.get("run_id")] = run_metrics
    return {"status": "success", "experiment_id": exp_id, "metrics": metrics}


# Datasets API
@router.get("/datasets")
def list_datasets():
    return {"status": "success", "datasets": ds_reg.list_datasets()}


@router.get("/datasets/{ds_id}")
def get_dataset(ds_id: str):
    ds = ds_reg.get_dataset(ds_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": "success", "dataset": ds}


@router.get("/datasets/{ds_id}/quality")
def get_dataset_quality(ds_id: str):
    ds = ds_reg.get_dataset(ds_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": "success", "quality_report": ds.get("quality_report", {})}


# Features API
@router.get("/features")
def list_features():
    return {"status": "success", "features": feat_reg.list_features()}


@router.get("/features/{feat_id}")
def get_feature(feat_id: str):
    feat = feat_reg.get_feature(feat_id)
    if not feat:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"status": "success", "feature": feat}


@router.get("/features/{feat_id}/lineage")
def get_feature_lineage(feat_id: str):
    feat = feat_reg.get_feature(feat_id)
    if not feat:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"status": "success", "lineage": feat.get("lineage", {})}


# Lineage Graph API
@router.get("/lineage/{run_id}")
def get_run_lineage(run_id: str):
    graph = lineage_tr.get_lineage(run_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Lineage graph not found")
    return {"status": "success", "lineage_graph": graph}
