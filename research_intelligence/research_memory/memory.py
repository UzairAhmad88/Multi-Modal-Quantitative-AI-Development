"""
Research Memory and Finding Store for Research Intelligence.
Stores persistent findings, failure logs, experiment lineage graphs, deduplication indices,
and enforces evidence-based research language validation.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import datetime
import uuid
import re
from research_intelligence.experiment_manager.manager import ExperimentRecord, ExperimentConfig


class ResearchClaimValidator:
    """Validates research statements to ensure evidence-based terminology and block prohibited promotional claims."""

    PROHIBITED_TERMS = [
        "guaranteed",
        "guaranteed return",
        "risk-free",
        "proven profitable",
        "certain",
        "always works",
        "100% accurate",
    ]

    ALLOWED_TERMS = ["observed", "measured", "associated", "consistent with", "inconclusive"]

    @classmethod
    def validate_statement(cls, statement: str) -> bool:
        lower_stmt = statement.lower()
        for term in cls.PROHIBITED_TERMS:
            if term in lower_stmt:
                raise ValueError(f"Research claim contains prohibited promotional term: '{term}'. Must use evidence-based language.")
        return True


@dataclass
class ResearchFinding:
    finding_id: str
    experiment_id: str
    statement: str
    evidence: str
    metrics: Dict[str, Any]
    period: str
    confidence: float
    limitations: str
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def __post_init__(self):
        ResearchClaimValidator.validate_statement(self.statement)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResearchMemory:
    """Memory store for experiments, findings, failure records, deduplication, and research lineage graphs."""

    def __init__(self):
        self._experiments: Dict[str, ExperimentRecord] = {}
        self._findings: Dict[str, ResearchFinding] = {}
        self._failures: List[Dict[str, Any]] = []

    def store_experiment(self, record: ExperimentRecord):
        self._experiments[record.experiment_id] = record
        if record.diagnostics:
            self._failures.append({
                "experiment_id": record.experiment_id,
                "model": record.config.model,
                "dataset": record.config.dataset,
                "features": record.config.features,
                "failure_stage": record.diagnostics.stage,
                "error": record.diagnostics.error_message,
                "timestamp": record.diagnostics.timestamp,
            })

    def store_finding(
        self,
        experiment_id: str,
        statement: str,
        evidence: str,
        metrics: Dict[str, Any],
        period: str,
        confidence: float,
        limitations: str,
    ) -> ResearchFinding:
        fid = f"FND-{datetime.date.today().year}-{uuid.uuid4().hex[:6].upper()}"
        finding = ResearchFinding(
            finding_id=fid,
            experiment_id=experiment_id,
            statement=statement,
            evidence=evidence,
            metrics=metrics,
            period=period,
            confidence=confidence,
            limitations=limitations,
        )
        self._findings[fid] = finding
        return finding

    def find_duplicate(self, config: ExperimentConfig) -> Optional[ExperimentRecord]:
        """Returns existing completed experiment if identical dataset, features, model, and seed are found."""
        for record in self._experiments.values():
            if record.results and not record.diagnostics:
                cfg = record.config
                if (
                    cfg.dataset == config.dataset
                    and cfg.model == config.model
                    and set(cfg.features) == set(config.features)
                    and cfg.random_seed == config.random_seed
                ):
                    return record
        return None

    def find_similar(self, config: ExperimentConfig) -> List[ExperimentRecord]:
        """Finds historical experiments sharing model, dataset, or features."""
        similar = []
        for record in self._experiments.values():
            cfg = record.config
            if cfg.model == config.model or cfg.dataset == config.dataset:
                similar.append(record)
        return similar

    def get_lineage(self, experiment_id: str) -> Dict[str, Any]:
        """Builds lineage graph structure for experiment."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            return {}

        findings = [f.to_dict() for f in self._findings.values() if f.experiment_id == experiment_id]
        return {
            "hypothesis_id": exp.config.hypothesis_id,
            "experiment_id": experiment_id,
            "dataset": exp.config.dataset,
            "features": exp.config.features,
            "model": exp.config.model,
            "versions": asdict(exp.config.versions),
            "findings": findings,
            "status": exp.status.value,
        }

    def get_graph_data(self) -> Dict[str, Any]:
        """Prepares nodes and edges for backend dashboard UI graph visualizations."""
        nodes = []
        edges = []

        for exp in self._experiments.values():
            nodes.append({"id": exp.experiment_id, "label": exp.config.name, "type": "EXPERIMENT"})
            nodes.append({"id": f"HYP-{exp.config.hypothesis_id}", "label": exp.config.hypothesis_id, "type": "HYPOTHESIS"})
            edges.append({"source": f"HYP-{exp.config.hypothesis_id}", "target": exp.experiment_id, "relation": "TESTS"})

        for fnd in self._findings.values():
            nodes.append({"id": fnd.finding_id, "label": fnd.statement[:30], "type": "FINDING"})
            edges.append({"source": fnd.experiment_id, "target": fnd.finding_id, "relation": "PRODUCES"})

        return {"nodes": nodes, "edges": edges}

    def list_findings() -> List[ResearchFinding]:
        return list(self._findings.values())

    def list_failures() -> List[Dict[str, Any]]:
        return self._failures
