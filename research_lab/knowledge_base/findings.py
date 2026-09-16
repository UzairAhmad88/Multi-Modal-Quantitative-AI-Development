"""
Finding Dataclass: Standardized format for indexing research discoveries, evidence, and limitations.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List
from datetime import datetime
import uuid


@dataclass
class Finding:
    finding_id: str = field(default_factory=lambda: f"FIND-{uuid.uuid4().hex[:8].upper()}")
    experiment_id: str = "EXP-001"
    statement: str = ""
    evidence: List[str] = field(default_factory=list)
    confidence: str = "RESEARCH_NOTE"  # OBSERVED, DERIVED, HYPOTHESIZED, UNCERTAIN
    limitations: str = "Subject to finite backtest sample size."
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
