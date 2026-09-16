"""
Domain Result Objects for Model Monitoring & Research Health OS.
"""

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .alerts import MonitoringAlert


class DriftMetricResult(BaseModel):
    feature_name: str
    psi_score: float
    ks_statistic: float
    ks_pvalue: float
    wasserstein_distance: float
    is_drifted: bool
    severity: str  # "NONE", "MODERATE", "SIGNIFICANT"
    evidence: Dict[str, Any] = Field(default_factory=dict)


class ConceptDriftResult(BaseModel):
    method: str  # "DDM", "EDDM", "PAGE_HINKLEY"
    drift_detected: bool
    warning_detected: bool
    change_point_index: Optional[int] = None
    metric_name: str
    current_value: float
    threshold: float
    evidence: Dict[str, Any] = Field(default_factory=dict)


class AlphaDecayResult(BaseModel):
    rolling_ic: float
    rank_ic: float
    ic_half_life_days: float
    ic_decay_pct: float
    rolling_sharpe: float
    sharpe_decay_pct: float
    max_drawdown_pct: float
    is_decay_flagged: bool


class RegimeShiftResult(BaseModel):
    current_regime: str  # e.g., "BULL", "BEAR", "HIGH_VOLATILITY", "STAGNANT"
    regime_transition_prob: float
    volatility_jump_ratio: float
    is_regime_shift_detected: bool


class ResearchHealthScore(BaseModel):
    overall_health_score: float  # 0 to 100
    data_quality_score: float    # 0 to 100
    feature_stability_score: float  # 0 to 100
    concept_stability_score: float  # 0 to 100
    alpha_retention_score: float   # 0 to 100
    risk_compliance_score: float   # 0 to 100
    status: str  # "HEALTHY", "WARNING", "CRITICAL"
    summary: str


class MonitoringResult(BaseModel):
    monitoring_id: str
    experiment_id: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    baseline_dataset_id: Optional[str] = None
    target_dataset_id: Optional[str] = None
    data_drift_results: List[DriftMetricResult] = Field(default_factory=list)
    concept_drift_results: List[ConceptDriftResult] = Field(default_factory=list)
    alpha_decay: Optional[AlphaDecayResult] = None
    regime_shift: Optional[RegimeShiftResult] = None
    health_score: ResearchHealthScore
    alerts: List[MonitoringAlert] = Field(default_factory=list)
    artifacts: Dict[str, str] = Field(default_factory=dict)
