"""
Validation Domain Result Objects & Summary Representations for Walk-Forward OS.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ValidationRun:
    """Represents an execution run of temporal walk-forward cross-validation."""

    run_id: str
    experiment_id: str
    method: str  # EXPANDING, ROLLING, ANCHORED, PURGED_CV
    total_folds: int
    train_window_size: int
    validation_window_size: int
    test_window_size: int
    purge_period: int
    embargo_period: int
    config_hash: str
    is_locked: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationResult:
    """Comprehensive container for walk-forward OOS metrics, fold evaluation, leakage checks, and robustness."""

    validation_id: str
    experiment_id: str
    method: str
    status: str  # COMPLETED, FAILED, LEAKAGE_DETECTED, INVALID, TEST_LOCKED
    config_hash: str
    windows: List[Dict[str, Any]] = field(default_factory=list)
    oos_metrics: Dict[str, Any] = field(default_factory=dict)
    leakage_audit: Dict[str, Any] = field(default_factory=dict)
    robustness_metrics: Dict[str, Any] = field(default_factory=dict)
    regime_analysis: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
