"""
Schemas for Statistical Validation, Bootstrap, Significance, Stability, and Research Integrity.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class IntegrityFlagSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class IntegrityFlagType(str, Enum):
    LOOK_AHEAD_RISK = "LOOK_AHEAD_RISK"
    DATA_LEAKAGE = "DATA_LEAKAGE"
    MULTIPLE_TESTING = "MULTIPLE_TESTING"
    SMALL_SAMPLE = "SMALL_SAMPLE"
    PARAMETER_INSTABILITY = "PARAMETER_INSTABILITY"
    REGIME_INSTABILITY = "REGIME_INSTABILITY"
    HIGH_COST_SENSITIVITY = "HIGH_COST_SENSITIVITY"
    TRAIN_TEST_GAP = "TRAIN_TEST_GAP"


class IntegrityFlag(BaseModel):
    flag_type: IntegrityFlagType
    severity: IntegrityFlagSeverity
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class AssumptionCheck(BaseModel):
    assumption: str
    status: str  # PASS, WARNING, FAIL
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class BootstrapResult(BaseModel):
    metric: str
    estimate: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.95
    iterations: int = 1000
    block_size: int = 20
    random_seed: int = 42
    method: str = "stationary_block"


class SignificanceResult(BaseModel):
    test_name: str
    null_hypothesis: str
    alternative_hypothesis: str
    test_statistic: float
    p_value: float
    effect_size: float
    effect_size_method: str = "cohens_d"
    sample_size: int
    is_statistically_significant: bool = False


class MultipleTestingResult(BaseModel):
    method: str  # Bonferroni, Holm, Benjamini-Hochberg
    number_of_tests: int
    raw_p_values: List[float]
    adjusted_p_values: List[float]
    rejected_nulls: List[bool]


class SubperiodWindow(BaseModel):
    window_index: int
    start_date: str
    end_date: str
    sample_size: int
    cagr: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float


class StabilityResult(BaseModel):
    subperiods: List[SubperiodWindow] = Field(default_factory=list)
    sharpe_std: float = 0.0
    drawdown_std: float = 0.0
    stability_score: float = 0.0  # 0 to 100


class StatisticalValidation(BaseModel):
    validation_id: str
    experiment_id: str
    backtest_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    dataset_id: str
    validation_status: str = "COMPLETED"  # VALID, INSUFFICIENT_SAMPLE, INVALID, etc.
    configuration_hash: str = ""
    sample_size: int = 0
    basic_statistics: Dict[str, Any] = Field(default_factory=dict)
    confidence_intervals: Dict[str, Any] = Field(default_factory=dict)
    bootstrap_results: List[BootstrapResult] = Field(default_factory=list)
    significance_results: List[SignificanceResult] = Field(default_factory=list)
    multiple_testing_result: Optional[MultipleTestingResult] = None
    stability_result: Optional[StabilityResult] = None
    assumption_checks: List[AssumptionCheck] = Field(default_factory=list)
    integrity_flags: List[IntegrityFlag] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
