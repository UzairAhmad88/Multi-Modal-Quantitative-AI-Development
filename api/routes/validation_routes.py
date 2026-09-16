"""
REST API Routes for Research Validation (Phase 13).
Provides audit query and execution endpoints for leakage detection, walk-forward CV, stress tests,
statistical evidence, bootstrap CIs, overfitting diagnostics, and reproducibility hashes.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, List, Any, Optional
from validation.orchestrator import ValidationPipeline

router = APIRouter(prefix="/validation", tags=["Research Validation"])

_pipeline = ValidationPipeline()


@router.get("/overview")
def get_validation_overview() -> Dict[str, Any]:
    return {
        "status": "active",
        "system": "Research-Grade Validation Engine",
        "leakage_detection": "ENABLED",
        "walk_forward_cv": "ENABLED",
        "bootstrap_resampling": "ENABLED (1000 iter)",
        "real_money_trading_enabled": False,
    }


@router.get("/experiments/{id}")
def get_experiment_validation(id: str) -> Dict[str, Any]:
    res = _pipeline.run_full_validation_suite(experiment_id=id)
    return res["validation_summary"]


@router.post("/run")
def run_validation(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    exp_id = payload.get("experiment_id", "EXP-2026-000001")
    res = _pipeline.run_full_validation_suite(experiment_id=exp_id, config=payload)
    return res


@router.get("/leakage/{id}")
def get_leakage_audit(id: str) -> Dict[str, Any]:
    res = _pipeline.run_full_validation_suite(experiment_id=id)
    return res["leakage_detection"]


@router.get("/walk-forward/{id}")
def get_walk_forward_results(id: str) -> Dict[str, Any]:
    res = _pipeline.run_full_validation_suite(experiment_id=id)
    return res["walk_forward"]


@router.get("/stress/{id}")
def get_stress_test_results(id: str) -> Dict[str, Any]:
    res = _pipeline.run_full_validation_suite(experiment_id=id)
    return res["stress_testing"]


@router.get("/statistics/{id}")
def get_statistical_test_results(id: str) -> Dict[str, Any]:
    res = _pipeline.run_full_validation_suite(experiment_id=id)
    return {
        "statistical_tests": res["statistical_tests"],
        "snooping_warning": res["snooping_warning"],
        "bootstrap": res["bootstrap"],
        "monte_carlo": res["monte_carlo"],
    }


@router.get("/robustness/{id}")
def get_robustness_results(id: str) -> Dict[str, Any]:
    res = _pipeline.run_full_validation_suite(experiment_id=id)
    return res["sensitivity"]


@router.get("/reproducibility/{id}")
def get_reproducibility_hash(id: str) -> Dict[str, Any]:
    res = _pipeline.run_full_validation_suite(experiment_id=id)
    return res["reproducibility"]
