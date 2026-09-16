"""
Schemas for Quant Research Knowledge Records, Claims, Journal Entries, Reproducibility Cards, and Families.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ClaimStatus(str, Enum):
    OBSERVED = "OBSERVED"
    STATISTICAL = "STATISTICAL"
    HYPOTHESIS = "HYPOTHESIS"
    UNSUPPORTED = "UNSUPPORTED"
    REJECTED = "REJECTED"


class JournalType(str, Enum):
    OBSERVATION = "OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"
    DECISION = "DECISION"
    RESULT = "RESULT"
    FAILURE = "FAILURE"
    LIMITATION = "LIMITATION"
    FOLLOW_UP = "FOLLOW_UP"


class ReproducibilityCard(BaseModel):
    card_id: str
    experiment_id: str
    code_version: str = "git-main"
    dataset_id: str
    dataset_version: str
    feature_version: str
    model_version: str
    configuration_hash: str
    random_seed: int = 42
    environment_info: Dict[str, str] = Field(default_factory=dict)
    execution_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    artifact_locations: Dict[str, str] = Field(default_factory=dict)


class ResearchClaim(BaseModel):
    claim_id: str
    statement: str
    evidence_experiment_ids: List[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.OBSERVED
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    author: str = "Quant Researcher"
    notes: Optional[str] = None


class ResearchJournalEntry(BaseModel):
    journal_id: str
    experiment_id: Optional[str] = None
    entry_type: JournalType = JournalType.OBSERVATION
    content: str
    linked_artifacts: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    author: str = "Quant Researcher"


class ExperimentFamily(BaseModel):
    family_id: str
    name: str
    parent_experiment_id: str
    child_experiment_ids: List[str] = Field(default_factory=list)
    ablation_modality_map: Dict[str, List[str]] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ResearchKnowledgeRecord(BaseModel):
    knowledge_id: str
    experiment_id: str
    run_id: Optional[str] = None
    workflow_id: Optional[str] = None
    campaign_id: Optional[str] = None
    dataset_id: str
    feature_set_id: str
    model_id: str
    strategy_id: str
    backtest_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    report_id: Optional[str] = None

    # Metadata
    research_question: str = ""
    hypothesis: str = ""
    modalities: List[str] = Field(default_factory=lambda: ["market"])
    status: str = "COMPLETED"
    configuration_hash: str = ""

    # Metrics
    metrics: Dict[str, Any] = Field(default_factory=dict)
    risk_metrics: Dict[str, Any] = Field(default_factory=dict)
    failure_details: Optional[Dict[str, Any]] = None

    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
