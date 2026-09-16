"""
Metadata Extractor & Automatic Experiment Indexer.
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from knowledge.schemas.knowledge_record import ResearchKnowledgeRecord, ReproducibilityCard
from research_lab.schemas.experiment_schema import Experiment


class MetadataExtractor:
    """
    Extracts structured metadata from completed or failed experiments and constructs Reproducibility Cards.
    """

    @staticmethod
    def extract_record(
        exp: Experiment,
        metrics: Dict[str, Any] = None,
        risk_metrics: Dict[str, Any] = None,
        failure_details: Optional[Dict[str, Any]] = None,
    ) -> ResearchKnowledgeRecord:
        metrics_data = metrics or {}
        risk_data = risk_metrics or {}

        # Handle hypothesis dictionary or object
        q = ""
        h = ""
        if isinstance(exp.hypothesis, dict):
            q = exp.hypothesis.get("research_question", "")
            h = exp.hypothesis.get("hypothesis", "")
        elif hasattr(exp.hypothesis, "research_question"):
            q = exp.hypothesis.research_question
            h = exp.hypothesis.hypothesis

        return ResearchKnowledgeRecord(
            knowledge_id=f"KNOW-{exp.experiment_id}",
            experiment_id=exp.experiment_id,
            dataset_id=exp.dataset_id,
            feature_set_id=exp.feature_version,
            model_id=exp.model_version,
            strategy_id=exp.strategy_id,
            backtest_id=f"BT-{exp.experiment_id}",
            evaluation_id=f"EVAL-{exp.experiment_id}",
            report_id=f"RPT-{exp.experiment_id}",
            research_question=q,
            hypothesis=h,
            modalities=exp.tags or ["market"],
            status=exp.status.value if hasattr(exp.status, "value") else str(exp.status),
            configuration_hash=exp.configuration_hash,
            metrics=metrics_data,
            risk_metrics=risk_data,
            failure_details=failure_details,
        )

    @staticmethod
    def create_reproducibility_card(exp: Experiment) -> ReproducibilityCard:
        return ReproducibilityCard(
            card_id=f"CARD-{exp.experiment_id}",
            experiment_id=exp.experiment_id,
            code_version="git-main",
            dataset_id=exp.dataset_id,
            dataset_version="v1.0.0",
            feature_version=exp.feature_version,
            model_version=exp.model_version,
            configuration_hash=exp.configuration_hash or "SHA256-INIT",
            random_seed=exp.random_seed,
            environment_info={
                "python": "3.11+",
                "platform": "win32",
                "framework": "PyTorch / scikit-learn",
            },
            artifact_locations={
                "report": f"reports/research/exp_{exp.experiment_id}.md",
                "checkpoint": f"artifacts/experiments/{exp.experiment_id}/",
            },
        )
