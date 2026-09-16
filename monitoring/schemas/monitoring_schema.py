"""
Pydantic Schemas for Monitoring API Requests and Responses.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MonitoringRunRequest(BaseModel):
    experiment_id: str = Field(default="EXP-001")
    psi_threshold: float = Field(default=0.10)
    ks_threshold: float = Field(default=0.05)
    feature_columns: Optional[List[str]] = Field(default=None)


class MonitoringRunResponse(BaseModel):
    monitoring_id: str
    experiment_id: str
    timestamp: str
    overall_health_score: float
    status: str
    drifted_features_count: int
    alerts_count: int
    summary: str


class DriftCheckRequest(BaseModel):
    baseline_values: List[float]
    target_values: List[float]
    feature_name: str = Field(default="feature_1")


class DriftCheckResponse(BaseModel):
    feature_name: str
    psi_score: float
    ks_statistic: float
    ks_pvalue: float
    wasserstein_distance: float
    is_drifted: bool
    severity: str
