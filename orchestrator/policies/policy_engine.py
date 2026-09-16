"""
Research Policy Engine for Workflow Verification & Safety Rules.
"""

from typing import Dict, Any, List
from orchestrator.schemas.workflow_schema import PolicyResult
from orchestrator.gates.gates import (
    DataGate,
    LeakageGate,
    FeatureGate,
    ModelGate,
    BacktestGate,
    RiskGate,
    EvaluationGate,
)


class ResearchPolicyEngine:
    """
    Evaluates research safety policies across context:
    - Minimum observations check
    - Test-set protection rule
    - Maximum turnover check
    - Maximum leverage limit
    """

    def __init__(self):
        self.gates = [
            DataGate,
            LeakageGate,
            FeatureGate,
            ModelGate,
            BacktestGate,
            RiskGate,
            EvaluationGate,
        ]

    def evaluate_all(self, context: Dict[str, Any]) -> List[PolicyResult]:
        results = []

        # Run gates
        results.append(DataGate.verify(context))
        results.append(LeakageGate.verify(context))
        results.append(FeatureGate.verify(context))
        results.append(ModelGate.verify(context))
        results.append(BacktestGate.verify(context))
        results.append(RiskGate.verify(context))
        results.append(EvaluationGate.verify(context))

        # Additional specific policy rules
        min_obs = context.get("min_observations", 252)
        actual_obs = context.get("data_observations", 500)
        if actual_obs < min_obs:
            results.append(
                PolicyResult(
                    policy="MinObservationsPolicy",
                    status="FAIL",
                    message=f"Insufficient observations: {actual_obs} < required {min_obs}",
                )
            )
        else:
            results.append(
                PolicyResult(
                    policy="MinObservationsPolicy",
                    status="PASS",
                    message=f"Observations requirement satisfied ({actual_obs} >= {min_obs})",
                )
            )

        max_leverage = context.get("max_leverage", 2.0)
        actual_leverage = context.get("leverage", 1.0)
        if actual_leverage > max_leverage:
            results.append(
                PolicyResult(
                    policy="MaxLeveragePolicy",
                    status="FAIL",
                    message=f"Leverage violation: {actual_leverage} > max {max_leverage}",
                )
            )
        else:
            results.append(
                PolicyResult(
                    policy="MaxLeveragePolicy",
                    status="PASS",
                    message=f"Leverage within allowed limits ({actual_leverage} <= {max_leverage})",
                )
            )

        return results
