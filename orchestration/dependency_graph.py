"""
Dependency Graph for 17-Stage Quantitative Research Pipeline.
Enforces DAG execution dependencies so stages execute strictly after prerequisites complete.
"""

from typing import Dict, List, Set, Any
from enum import Enum


class PipelineStage(str, Enum):
    CONFIGURATION = "CONFIGURATION"
    DATA = "DATA"
    DATA_VALIDATION = "DATA_VALIDATION"
    FEATURE_ENGINEERING = "FEATURE_ENGINEERING"
    DATASET_SPLIT = "DATASET_SPLIT"
    MODEL_TRAINING = "MODEL_TRAINING"
    PREDICTION = "PREDICTION"
    SIGNAL_GENERATION = "SIGNAL_GENERATION"
    PORTFOLIO_CONSTRUCTION = "PORTFOLIO_CONSTRUCTION"
    BACKTEST = "BACKTEST"
    VALIDATION = "VALIDATION"
    ROBUSTNESS = "ROBUSTNESS"
    STRESS_TESTING = "STRESS_TESTING"
    STATISTICAL_ANALYSIS = "STATISTICAL_ANALYSIS"
    RESEARCH_FINDING = "RESEARCH_FINDING"
    REPORT = "REPORT"
    ARTIFACT_REGISTRATION = "ARTIFACT_REGISTRATION"


class DependencyGraph:
    """DAG manager defining dependencies and execution ordering for 17 pipeline stages."""

    STAGE_DEPENDENCIES: Dict[PipelineStage, List[PipelineStage]] = {
        PipelineStage.CONFIGURATION: [],
        PipelineStage.DATA: [PipelineStage.CONFIGURATION],
        PipelineStage.DATA_VALIDATION: [PipelineStage.DATA],
        PipelineStage.FEATURE_ENGINEERING: [PipelineStage.DATA_VALIDATION],
        PipelineStage.DATASET_SPLIT: [PipelineStage.FEATURE_ENGINEERING],
        PipelineStage.MODEL_TRAINING: [PipelineStage.DATASET_SPLIT],
        PipelineStage.PREDICTION: [PipelineStage.MODEL_TRAINING],
        PipelineStage.SIGNAL_GENERATION: [PipelineStage.PREDICTION],
        PipelineStage.PORTFOLIO_CONSTRUCTION: [PipelineStage.SIGNAL_GENERATION],
        PipelineStage.BACKTEST: [PipelineStage.PORTFOLIO_CONSTRUCTION],
        PipelineStage.VALIDATION: [PipelineStage.BACKTEST],
        PipelineStage.ROBUSTNESS: [PipelineStage.VALIDATION],
        PipelineStage.STRESS_TESTING: [PipelineStage.ROBUSTNESS],
        PipelineStage.STATISTICAL_ANALYSIS: [PipelineStage.STRESS_TESTING],
        PipelineStage.RESEARCH_FINDING: [PipelineStage.STATISTICAL_ANALYSIS],
        PipelineStage.REPORT: [PipelineStage.RESEARCH_FINDING],
        PipelineStage.ARTIFACT_REGISTRATION: [PipelineStage.REPORT],
    }

    @classmethod
    def get_ordered_stages(cls) -> List[PipelineStage]:
        """Returns topological execution order for all 17 stages."""
        return list(cls.STAGE_DEPENDENCIES.keys())

    @classmethod
    def get_prerequisites(cls, stage: PipelineStage) -> List[PipelineStage]:
        return cls.STAGE_DEPENDENCIES.get(stage, [])

    @classmethod
    def is_stage_ready(cls, stage: PipelineStage, completed_stages: Set[PipelineStage]) -> bool:
        prereqs = cls.get_prerequisites(stage)
        return all(p in completed_stages for p in prereqs)
