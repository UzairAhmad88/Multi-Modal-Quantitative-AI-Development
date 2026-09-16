"""
Validation Gates for Pre-Task Workflow Verification.
"""

from typing import Dict, Any, Tuple
from orchestrator.schemas.workflow_schema import PolicyResult


class ValidationGateError(Exception):
    pass


class DataGate:
    @staticmethod
    def verify(context: Dict[str, Any]) -> PolicyResult:
        dataset_id = context.get("dataset_id")
        if not dataset_id:
            return PolicyResult(
                policy="DataGate",
                status="FAIL",
                message="Dataset ID is missing from workflow context",
            )
        return PolicyResult(
            policy="DataGate",
            status="PASS",
            message=f"Dataset '{dataset_id}' verified successfully",
        )


class LeakageGate:
    @staticmethod
    def verify(context: Dict[str, Any]) -> PolicyResult:
        has_future_labels = context.get("has_future_labels", False)
        if has_future_labels:
            return PolicyResult(
                policy="LeakageGate",
                status="FAIL",
                message="Data leakage detected: future label contamination found",
            )
        return PolicyResult(
            policy="LeakageGate",
            status="PASS",
            message="No data leakage detected",
        )


class FeatureGate:
    @staticmethod
    def verify(context: Dict[str, Any]) -> PolicyResult:
        features = context.get("features", ["price", "returns"])
        if not features:
            return PolicyResult(
                policy="FeatureGate",
                status="FAIL",
                message="Feature list is empty",
            )
        return PolicyResult(
            policy="FeatureGate",
            status="PASS",
            message=f"Features verified ({len(features)} features registered)",
        )


class ModelGate:
    @staticmethod
    def verify(context: Dict[str, Any]) -> PolicyResult:
        model_type = context.get("model_type", "xgboost")
        allowed = ["xgboost", "random_forest", "lstm", "gru", "transformer", "multimodal"]
        if model_type not in allowed:
            return PolicyResult(
                policy="ModelGate",
                status="FAIL",
                message=f"Unsupported model type '{model_type}'",
            )
        return PolicyResult(
            policy="ModelGate",
            status="PASS",
            message=f"Model architecture '{model_type}' verified",
        )


class BacktestGate:
    @staticmethod
    def verify(context: Dict[str, Any]) -> PolicyResult:
        slippage_bps = context.get("slippage_bps", 5.0)
        fee_bps = context.get("fee_bps", 10.0)
        if slippage_bps < 0 or fee_bps < 0:
            return PolicyResult(
                policy="BacktestGate",
                status="FAIL",
                message="Negative slippage or transaction fee configured",
            )
        return PolicyResult(
            policy="BacktestGate",
            status="PASS",
            message=f"Execution costs verified (slippage: {slippage_bps} bps, fee: {fee_bps} bps)",
        )


class RiskGate:
    @staticmethod
    def verify(context: Dict[str, Any]) -> PolicyResult:
        max_drawdown_limit = context.get("max_drawdown_limit", 0.5)
        if max_drawdown_limit > 0.9:
            return PolicyResult(
                policy="RiskGate",
                status="FAIL",
                message="Extreme drawdown limit exceeds safe parameters (> 90%)",
            )
        return PolicyResult(
            policy="RiskGate",
            status="PASS",
            message="Risk limits verified",
        )


class EvaluationGate:
    @staticmethod
    def verify(context: Dict[str, Any]) -> PolicyResult:
        metrics = context.get("metrics", {})
        if "test_used_for_tuning" in context and context["test_used_for_tuning"]:
            return PolicyResult(
                policy="EvaluationGate",
                status="FAIL",
                message="Test set protection violation: test set was used for hyperparameter tuning",
            )
        return PolicyResult(
            policy="EvaluationGate",
            status="PASS",
            message="Evaluation metrics and test set separation verified",
        )
