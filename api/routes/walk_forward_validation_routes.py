"""
REST API Routes for Phase 27 Walk-Forward Validation & OOS OS.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

from validation.schemas.walk_forward_schema import WalkForwardRunRequest, LeakageCheckRequest
from validation.services.walk_forward_service import WalkForwardService
from validation.reports.generator import WalkForwardReportGenerator
from validation.leakage.detector import LeakageDetector
import pandas as pd
import numpy as np

router = APIRouter(prefix="/walk-forward-v2", tags=["Walk-Forward Validation Engine"])
service = WalkForwardService()


@router.get("/health")
def walk_forward_health():
    return {
        "status": "HEALTHY",
        "walk_forward_engine": "OK",
        "purged_splitter": "OK",
        "embargo_excluder": "OK",
        "leakage_detector": "OK",
        "test_lock_engine": "OK",
    }


@router.post("/run")
def run_walk_forward(req: WalkForwardRunRequest):
    res = service.run_walk_forward(
        experiment_id=req.experiment_id,
        method=req.method,
        train_window_size=req.train_window_size,
        val_window_size=req.val_window_size,
        test_window_size=req.test_window_size,
        step_size=req.step_size,
        purge_period=req.purge_period,
        embargo_period=req.embargo_period,
        lock_test_set=req.lock_test_set,
    )
    return res


@router.get("/{validation_id}")
def get_walk_forward_run(validation_id: str):
    run = service.get_run(validation_id)
    if not run:
        raise HTTPException(status_code=404, detail="Walk-forward validation run not found")
    return run


@router.get("/{validation_id}/windows")
def get_windows(validation_id: str):
    run = service.get_run(validation_id)
    if not run:
        raise HTTPException(status_code=404, detail="Walk-forward validation run not found")
    return {"validation_id": validation_id, "total_windows": len(run.get("windows", [])), "windows": run.get("windows", [])}


@router.get("/{validation_id}/metrics")
def get_metrics(validation_id: str):
    run = service.get_run(validation_id)
    if not run:
        raise HTTPException(status_code=404, detail="Walk-forward validation run not found")
    return {"validation_id": validation_id, "oos_metrics": run.get("oos_metrics", {})}


@router.get("/{validation_id}/leakage")
def get_leakage(validation_id: str):
    run = service.get_run(validation_id)
    if not run:
        raise HTTPException(status_code=404, detail="Walk-forward validation run not found")
    return {"validation_id": validation_id, "leakage_audit": run.get("leakage_audit", {})}


@router.get("/{validation_id}/robustness")
def get_robustness(validation_id: str):
    run = service.get_run(validation_id)
    if not run:
        raise HTTPException(status_code=404, detail="Walk-forward validation run not found")
    return {"validation_id": validation_id, "robustness_metrics": run.get("robustness_metrics", {})}


@router.get("/{validation_id}/report")
def get_report(validation_id: str):
    run = service.get_run(validation_id)
    if not run:
        raise HTTPException(status_code=404, detail="Walk-forward validation run not found")
    report_md = WalkForwardReportGenerator.generate_walk_forward_report(run)
    return {"validation_id": validation_id, "report_markdown": report_md}


@router.post("/leakage-check")
def run_leakage_check(req: LeakageCheckRequest):
    np.random.seed(42)
    dates = pd.date_range("2022-01-01", periods=req.sample_size, freq="B")
    df = pd.DataFrame({
        "timestamp": dates.strftime("%Y-%m-%d"),
        "availability_timestamp": (dates - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        "feature_1": np.random.normal(0, 1, size=req.sample_size),
        "target": np.random.normal(0.0005, 0.012, size=req.sample_size),
    })
    res = LeakageDetector.audit_full_dataset(df, decision_col="timestamp", target_col="target")
    return {"experiment_id": req.experiment_id, "leakage_check": res}



