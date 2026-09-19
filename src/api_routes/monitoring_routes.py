"""
REST API Routes for Model Monitoring, Drift Detection & Research Health OS.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from monitoring.schemas.monitoring_schema import (
    MonitoringRunRequest,
    MonitoringRunResponse,
    DriftCheckRequest,
    DriftCheckResponse,
)
from monitoring.services.monitoring_service import MonitoringService
from monitoring.data_drift.detector import DataDriftDetector

router = APIRouter(prefix="/monitoring", tags=["Model Monitoring OS"])
service = MonitoringService()


@router.get("/health", summary="Get Monitoring Engine Health")
def get_monitoring_health():
    return {
        "status": "healthy",
        "engine": "Model Monitoring & Research Health OS",
        "version": "1.0.0",
    }


@router.post("/run", response_model=MonitoringRunResponse, summary="Run Full Model Monitoring Audit")
def run_monitoring_audit(request: MonitoringRunRequest):
    result = service.run_monitoring(
        experiment_id=request.experiment_id,
        feature_columns=request.feature_columns,
    )
    drifted_count = sum(1 for d in result.data_drift_results if d.is_drifted)

    return MonitoringRunResponse(
        monitoring_id=result.monitoring_id,
        experiment_id=result.experiment_id,
        timestamp=result.timestamp,
        overall_health_score=result.health_score.overall_health_score,
        status=result.health_score.status,
        drifted_features_count=drifted_count,
        alerts_count=len(result.alerts),
        summary=result.health_score.summary,
    )


@router.get("/runs", summary="List All Monitoring Runs")
def list_monitoring_runs():
    return service.list_monitoring_runs()


@router.get("/{monitoring_id}", summary="Get Specific Monitoring Run Details")
def get_monitoring_run(monitoring_id: str):
    run = service.get_monitoring_run(monitoring_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Monitoring run '{monitoring_id}' not found.")
    return run.model_dump()


@router.post("/drift-check", response_model=DriftCheckResponse, summary="Perform Single Feature Drift Check")
def perform_feature_drift_check(request: DriftCheckRequest):
    detector = DataDriftDetector()
    results = detector.evaluate_feature_drift(
        baseline_df={request.feature_name: request.baseline_values},
        target_df={request.feature_name: request.target_values},
    )
    if not results:
        raise HTTPException(status_code=400, detail="Invalid data provided for drift check.")

    r = results[0]
    return DriftCheckResponse(
        feature_name=r.feature_name,
        psi_score=r.psi_score,
        ks_statistic=r.ks_statistic,
        ks_pvalue=r.ks_pvalue,
        wasserstein_distance=r.wasserstein_distance,
        is_drifted=r.is_drifted,
        severity=r.severity,
    )
