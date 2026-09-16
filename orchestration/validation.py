"""
Mandatory Pipeline Validation Gates for Orchestration OS.
"""

from typing import Any, Dict
from .pipeline_context import PipelineContext
from .exceptions import DataValidationError, LeakageGateError, RiskGateError, MonitoringGateError


class PipelineValidationGates:
    """Enforces critical validation gates across pipeline stages."""

    @staticmethod
    def audit_data_gate(context: PipelineContext) -> bool:
        if "DATA" not in context.stage_data:
            raise DataValidationError("DATA stage outputs missing.")
        m_df = context.stage_data["DATA"].get("market_df")
        if m_df is None or len(m_df) == 0:
            raise DataValidationError("Market dataset is empty.")
        return True

    @staticmethod
    def audit_leakage_gate(context: PipelineContext) -> bool:
        if "VALIDATION" not in context.stage_data:
            return True
        leak_res = context.stage_data["VALIDATION"].get("leakage", {})
        if leak_res.get("has_leakage", False) and context.config.get("strict_leakage", True):
            raise LeakageGateError("Critical feature leakage detected! Gate failed.")

        return True

    @staticmethod
    def audit_risk_gate(context: PipelineContext) -> bool:
        if "RISK" not in context.stage_data:
            return True
        r_out = context.stage_data["RISK"]
        var_val = abs(r_out.get("var_95", 0.0))
        max_allowed_var = context.config.get("max_allowed_var_95", 0.20)
        if var_val > max_allowed_var:
            raise RiskGateError(f"VaR 95% breach ({var_val:.2%} > max allowed {max_allowed_var:.2%}). Gate failed.")
        return True

    @staticmethod
    def audit_monitoring_gate(context: PipelineContext) -> bool:
        if "MONITORING" not in context.stage_data:
            return True
        h_score = context.stage_data["MONITORING"].get("health_score", 100.0)
        min_health = context.config.get("min_health_score", 50.0)
        if h_score < min_health:
            raise MonitoringGateError(f"Research Health Score critical ({h_score:.1f} < min required {min_health:.1f}). Gate failed.")
        return True
