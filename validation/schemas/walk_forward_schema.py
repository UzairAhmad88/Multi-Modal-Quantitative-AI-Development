"""
Pydantic Schemas for Walk-Forward OS API Requests & Responses.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class WalkForwardRunRequest(BaseModel):
    experiment_id: str = Field("EXP-001", json_schema_extra={"example": "EXP-001"})
    method: str = Field("EXPANDING", json_schema_extra={"example": "EXPANDING"})
    train_window_size: int = Field(250, json_schema_extra={"example": 250})
    val_window_size: int = Field(50, json_schema_extra={"example": 50})
    test_window_size: int = Field(50, json_schema_extra={"example": 50})
    step_size: int = Field(50, json_schema_extra={"example": 50})
    purge_period: int = Field(5, json_schema_extra={"example": 5})
    embargo_period: int = Field(5, json_schema_extra={"example": 5})
    lock_test_set: bool = Field(False, json_schema_extra={"example": False})


class LeakageCheckRequest(BaseModel):
    experiment_id: str = Field("EXP-001", json_schema_extra={"example": "EXP-001"})
    sample_size: int = Field(250, json_schema_extra={"example": 250})
