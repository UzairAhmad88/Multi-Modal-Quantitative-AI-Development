"""
Research Lineage Service for Pipeline DAG Tracing.
"""

from typing import Dict, Any, List, Optional
from knowledge.schemas.knowledge_record import ResearchKnowledgeRecord


class ResearchLineageService:
    """
    Traces DAG lineage across Dataset -> Feature -> Model -> Signal -> Portfolio -> Execution -> Backtest -> Evaluation -> Report.
    """

    @staticmethod
    def get_experiment_lineage(record: ResearchKnowledgeRecord) -> Dict[str, Any]:
        nodes = [
            {"id": record.dataset_id, "type": "Dataset", "label": f"Dataset ({record.dataset_id})"},
            {"id": record.feature_set_id, "type": "FeatureSet", "label": f"Feature Set ({record.feature_set_id})"},
            {"id": record.model_id, "type": "Model", "label": f"Model ({record.model_id})"},
            {"id": f"SIG-{record.experiment_id}", "type": "Signal", "label": "Alpha Signal"},
            {"id": f"PORT-{record.experiment_id}", "type": "Portfolio", "label": "Target Portfolio"},
            {"id": f"EXEC-{record.experiment_id}", "type": "Execution", "label": "Simulated Execution"},
            {"id": record.backtest_id or f"BT-{record.experiment_id}", "type": "Backtest", "label": "Backtest Engine"},
            {"id": record.evaluation_id or f"EVAL-{record.experiment_id}", "type": "Evaluation", "label": "Research Evaluation"},
            {"id": record.experiment_id, "type": "Experiment", "label": f"Experiment ({record.experiment_id})"},
            {"id": record.report_id or f"RPT-{record.experiment_id}", "type": "Report", "label": "Research Report"},
        ]

        edges = [
            {"from": record.dataset_id, "to": record.feature_set_id, "relation": "DERIVED_FROM"},
            {"from": record.feature_set_id, "to": record.model_id, "relation": "INPUT_TO"},
            {"from": record.model_id, "to": f"SIG-{record.experiment_id}", "relation": "GENERATES"},
            {"from": f"SIG-{record.experiment_id}", "to": f"PORT-{record.experiment_id}", "relation": "CONSTRUCTS"},
            {"from": f"PORT-{record.experiment_id}", "to": f"EXEC-{record.experiment_id}", "relation": "EXECUTES"},
            {"from": f"EXEC-{record.experiment_id}", "to": record.backtest_id or f"BT-{record.experiment_id}", "relation": "BACKTESTS"},
            {"from": record.backtest_id or f"BT-{record.experiment_id}", "to": record.evaluation_id or f"EVAL-{record.experiment_id}", "relation": "EVALUATED_BY"},
            {"from": record.evaluation_id or f"EVAL-{record.experiment_id}", "to": record.experiment_id, "relation": "RECORDED_IN"},
            {"from": record.experiment_id, "to": record.report_id or f"RPT-{record.experiment_id}", "relation": "COMPILES"},
        ]

        return {
            "experiment_id": record.experiment_id,
            "nodes": nodes,
            "edges": edges,
        }
