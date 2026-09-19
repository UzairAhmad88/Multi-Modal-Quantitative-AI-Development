"""
REST API Routes for Phase 24 Statistical Validation & Research Integrity OS.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import numpy as np

from validation.core.validation_manager import StatisticalValidationManager
from validation.reports.validation_report_generator import ValidationReportGenerator

router = APIRouter(prefix="/validation", tags=["Validation Engine"])
val_manager = StatisticalValidationManager()


class RunValidationRequest(BaseModel):
    experiment_id: str = "EXP-001"
    train_sharpe: float = 2.0
    random_seed: int = 42
    sample_size: int = 500


class CompareValidationRequest(BaseModel):
    validation_ids: List[str] = Field(default_factory=lambda: ["VAL-EXP-001", "VAL-EXP-002"])


@router.post("/run")
def run_validation(req: RunValidationRequest):
    np.random.seed(req.random_seed)
    returns = np.random.normal(loc=0.0008, scale=0.012, size=req.sample_size)
    val = val_manager.run_validation(
        experiment_id=req.experiment_id,
        returns=returns,
        train_sharpe=req.train_sharpe,
        random_seed=req.random_seed,
    )
    return val.model_dump()


@router.get("/{validation_id}")
def get_validation(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    return val.model_dump()


@router.get("/{validation_id}/statistics")
def get_validation_statistics(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    return {
        "basic_statistics": val.basic_statistics,
        "confidence_intervals": val.confidence_intervals,
    }


@router.get("/{validation_id}/bootstrap")
def get_validation_bootstrap(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    return {"bootstrap_results": [b.model_dump() for b in val.bootstrap_results]}


@router.get("/{validation_id}/significance")
def get_validation_significance(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    return {"significance_results": [s.model_dump() for s in val.significance_results]}


@router.get("/{validation_id}/stability")
def get_validation_stability(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    return {"stability_result": val.stability_result.model_dump() if val.stability_result else None}


@router.get("/{validation_id}/multiple-testing")
def get_validation_multiple_testing(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    return {"multiple_testing_result": val.multiple_testing_result.model_dump() if val.multiple_testing_result else None}


@router.get("/{validation_id}/diagnostics")
def get_validation_diagnostics(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    return {
        "assumption_checks": [c.model_dump() for c in val.assumption_checks],
        "integrity_flags": [f.model_dump() for f in val.integrity_flags],
    }


@router.get("/{validation_id}/report")
def get_validation_report(validation_id: str):
    val = val_manager.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation record not found")
    md = ValidationReportGenerator.generate_report_md(val)
    return {"validation_id": val.validation_id, "report_markdown": md}


@router.post("/compare")
def compare_validations(req: CompareValidationRequest):
    records = []
    for vid in req.validation_ids:
        val = val_manager.get_validation(vid)
        if val:
            records.append({
                "validation_id": val.validation_id,
                "experiment_id": val.experiment_id,
                "mean_return": val.basic_statistics.get("mean"),
                "sample_size": val.sample_size,
                "stability_score": val.stability_result.stability_score if val.stability_result else None,
            })
    return {"compared_count": len(records), "validations": records}


@router.get("/health")
def validation_health():
    return {
        "status": "HEALTHY",
        "validation_engine": "OK",
        "bootstrap_engine": "OK",
        "significance_tester": "OK",
        "multiple_testing_corrector": "OK",
        "stability_analyzer": "OK",
    }
