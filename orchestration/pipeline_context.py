"""
Pipeline Context Object for End-to-End Orchestration OS.
"""

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PipelineContext(BaseModel):
    experiment_id: str
    run_id: str
    dataset_version: str = "DATA-v1.0"
    feature_version: str = "FEAT-v1.0"
    model_version: str = "MODEL-v1.0"
    portfolio_version: str = "PORT-v1.0"
    risk_version: str = "RISK-v1.0"
    validation_version: str = "VAL-v1.0"
    monitoring_version: str = "MON-v1.0"
    configuration_hash: str = "00000000"
    git_commit: str = "HEAD"
    random_seed: int = 42
    start_time: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    status: str = "CREATED"
    symbols: List[str] = Field(default_factory=lambda: ["AAPL"])
    config: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, str] = Field(default_factory=dict)
    stage_data: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
