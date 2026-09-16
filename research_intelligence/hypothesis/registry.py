"""
Hypothesis Registry and Management for Research Intelligence.
Tracks hypothesis lifecycles, states, and pre-registration criteria.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import datetime
import uuid


class HypothesisState(str, Enum):
    DRAFT = "DRAFT"
    REGISTERED = "REGISTERED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    SUPPORTED = "SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class PreRegistrationSpec:
    """Pre-registration parameters defined prior to running experiments to minimize post-hoc bias."""
    objective: str
    dataset: str
    features: List[str]
    model: str
    evaluation_metrics: List[str]
    period: str
    expected_relationship: str


@dataclass
class Hypothesis:
    hypothesis_id: str
    title: str
    description: str
    research_question: str
    expected_effect: str
    null_hypothesis: str
    variables: List[str]
    dataset: str
    time_period: str
    status: HypothesisState = HypothesisState.DRAFT
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    preregistration: Optional[PreRegistrationSpec] = None
    experiment_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        if self.preregistration:
            data["preregistration"] = asdict(self.preregistration)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hypothesis":
        data = dict(data)
        if isinstance(data.get("status"), str):
            data["status"] = HypothesisState(data["status"])
        if data.get("preregistration") and isinstance(data["preregistration"], dict):
            data["preregistration"] = PreRegistrationSpec(**data["preregistration"])
        return cls(**data)


class HypothesisRegistry:
    """In-memory and file-backed registry for research hypotheses."""

    def __init__(self):
        self._hypotheses: Dict[str, Hypothesis] = {}

    def register(
        self,
        title: str,
        description: str,
        research_question: str,
        expected_effect: str,
        null_hypothesis: str,
        variables: List[str],
        dataset: str,
        time_period: str,
        preregistration: Optional[PreRegistrationSpec] = None,
    ) -> Hypothesis:
        hypo_id = f"HYP-{datetime.date.today().year}-{uuid.uuid4().hex[:6].upper()}"
        initial_state = HypothesisState.REGISTERED if preregistration else HypothesisState.DRAFT
        
        hypo = Hypothesis(
            hypothesis_id=hypo_id,
            title=title,
            description=description,
            research_question=research_question,
            expected_effect=expected_effect,
            null_hypothesis=null_hypothesis,
            variables=variables,
            dataset=dataset,
            time_period=time_period,
            status=initial_state,
            preregistration=preregistration,
        )
        self._hypotheses[hypo_id] = hypo
        return hypo

    def get(self, hypothesis_id: str) -> Optional[Hypothesis]:
        return self._hypotheses.get(hypothesis_id)

    def update_status(self, hypothesis_id: str, new_state: HypothesisState) -> Optional[Hypothesis]:
        hypo = self._hypotheses.get(hypothesis_id)
        if not hypo:
            return None
        hypo.status = new_state
        hypo.updated_at = datetime.datetime.utcnow().isoformat()
        return hypo

    def attach_experiment(self, hypothesis_id: str, experiment_id: str) -> bool:
        hypo = self._hypotheses.get(hypothesis_id)
        if not hypo:
            return False
        if experiment_id not in hypo.experiment_ids:
            hypo.experiment_ids.append(experiment_id)
        return True

    def list_hypotheses(self, state: Optional[HypothesisState] = None) -> List[Hypothesis]:
        if state:
            return [h for h in self._hypotheses.values() if h.status == state]
        return list(self._hypotheses.values())

    def search(self, query: str) -> List[Hypothesis]:
        q = query.lower()
        return [
            h for h in self._hypotheses.values()
            if q in h.title.lower() or q in h.description.lower() or q in h.research_question.lower()
        ]
