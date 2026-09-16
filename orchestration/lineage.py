"""
End-to-End Data-to-Report Lineage Tracer for Orchestration OS.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field
from .pipeline_context import PipelineContext


class ResearchLineageGraph(BaseModel):
    experiment_id: str
    run_id: str
    dataset_version: str
    feature_version: str
    model_id: str
    prediction_id: str
    alpha_id: str
    portfolio_id: str
    backtest_id: str
    risk_id: str
    monitoring_id: str
    report_id: str
    nodes: Dict[str, Any] = Field(default_factory=dict)


class LineageTracer:
    """Builds end-to-end lineage graphs for pipeline runs."""

    def trace_lineage(self, context: PipelineContext) -> ResearchLineageGraph:
        m_out = context.stage_data.get("TRAINING", {})
        a_out = context.stage_data.get("ALPHA", {})
        p_out = context.stage_data.get("PORTFOLIO", {})
        b_out = context.stage_data.get("BACKTEST", {})
        r_out = context.stage_data.get("RISK", {})
        mon_out = context.stage_data.get("MONITORING", {})

        return ResearchLineageGraph(
            experiment_id=context.experiment_id,
            run_id=context.run_id,
            dataset_version=context.dataset_version,
            feature_version=context.feature_version,
            model_id=m_out.get("model_id", f"MODEL-{context.experiment_id}"),
            prediction_id=f"PRED-{context.run_id[:8]}",
            alpha_id=f"ALPHA-{context.run_id[:8]}",
            portfolio_id=f"PORT-{context.run_id[:8]}",
            backtest_id=f"BACK-{context.run_id[:8]}",
            risk_id=f"RISK-{context.run_id[:8]}",
            monitoring_id=f"MON-{context.run_id[:8]}",
            report_id=f"REP-{context.run_id[:8]}",
            nodes={
                "symbols": context.symbols,
                "config_hash": context.configuration_hash,
                "random_seed": context.random_seed,
            },
        )
