"""
Experiment Planner & Matrix Generator.
"""

from typing import List, Dict, Any
import uuid
from orchestrator.schemas.workflow_schema import ResearchPlan
from research_lab.schemas.experiment_schema import Experiment
from research_lab.hypotheses.hypothesis_manager import Hypothesis


class ExperimentPlanner:
    """
    Generates a controlled matrix of independent traceable experiments from a ResearchPlan.
    """

    @staticmethod
    def generate_matrix(plan: ResearchPlan) -> List[Experiment]:
        experiments = []
        max_exp = plan.resource_budget.max_experiments
        count = 0

        for model in plan.models:
            for modality in plan.modalities:
                for strategy in plan.strategies:
                    for execution in plan.executions:
                        if count >= max_exp:
                            break
                        
                        exp_id = f"EXP-{uuid.uuid4().hex[:8].upper()}"
                        exp_name = f"{plan.name} - {model.upper()} ({modality})"

                        exp = Experiment(
                            experiment_id=exp_id,
                            name=exp_name,
                            description=f"Automated experiment for {model} with {modality} modality",
                            hypothesis=Hypothesis(
                                research_question=plan.objective,
                                hypothesis=plan.hypothesis,
                                expected_behavior="Statistically significant Sharpe improvement",
                                null_hypothesis="No difference in performance",
                                success_criteria="Sharpe >= 1.25",
                            ).to_dict(),
                            dataset_id=plan.dataset_id,
                            feature_version=f"FSET-{modality.upper()}-v1",
                            model_version=f"MDL-{model.upper()}-v1",
                            strategy_id=f"STRAT-{strategy.upper()}",
                            portfolio_config={"allocation_method": "equal_weight", "max_position": 0.2},
                            execution_config={"algorithm": execution, "slippage_bps": 5.0},
                            evaluation_config={"benchmark": "SP500", "risk_free_rate": 0.02},
                            tags=[model, modality, strategy, execution, "automated"],
                        )
                        experiments.append(exp)
                        count += 1

                    if count >= max_exp:
                        break
                if count >= max_exp:
                    break
            if count >= max_exp:
                break

        return experiments
