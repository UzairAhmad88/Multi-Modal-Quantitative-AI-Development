"""
Workflow Builder & Template Loader for Orchestrator Pipelines.
"""

import os
import yaml
import uuid
from typing import Dict, Any, List, Optional

from orchestrator.schemas.workflow_schema import Workflow, WorkflowTask, ResourceBudget
from orchestrator.core.states import WorkflowStatus, TaskStatus, Priority
from orchestrator.dependencies.dag_validator import DAGValidator


class WorkflowBuilder:
    """
    Constructs Workflow objects with validated DAG task dependencies.
    """

    @staticmethod
    def build_full_research_workflow(
        name: str = "Multimodal Quant Research Workflow",
        objective: str = "Full research pipeline execution",
        resource_budget: Optional[ResourceBudget] = None,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> Workflow:
        workflow_id = f"WF-{uuid.uuid4().hex[:8].upper()}"

        tasks = [
            WorkflowTask(
                task_id="data_validation",
                name="Data Validation Gate",
                task_type="DataValidationTask",
                depends_on=[],
            ),
            WorkflowTask(
                task_id="feature_engineering",
                name="Feature Store Generation",
                task_type="FeatureEngineeringTask",
                depends_on=["data_validation"],
            ),
            WorkflowTask(
                task_id="model_training",
                name="Model Factory Training",
                task_type="ModelTrainingTask",
                depends_on=["feature_engineering"],
            ),
            WorkflowTask(
                task_id="signal_generation",
                name="Alpha Signal Generation",
                task_type="SignalGenerationTask",
                depends_on=["model_training"],
            ),
            WorkflowTask(
                task_id="portfolio_construction",
                name="Portfolio Optimization",
                task_type="PortfolioConstructionTask",
                depends_on=["signal_generation"],
            ),
            WorkflowTask(
                task_id="execution_simulation",
                name="Market Execution Simulation",
                task_type="ExecutionSimulationTask",
                depends_on=["portfolio_construction"],
            ),
            WorkflowTask(
                task_id="backtest",
                name="Backtest Engine Execution",
                task_type="BacktestTask",
                depends_on=["execution_simulation"],
            ),
            WorkflowTask(
                task_id="risk_analysis",
                name="Risk Engine Analysis",
                task_type="RiskAnalysisTask",
                depends_on=["backtest"],
            ),
            WorkflowTask(
                task_id="research_evaluation",
                name="Research Evaluation & Statistics",
                task_type="ResearchEvaluationTask",
                depends_on=["backtest"],
            ),
            WorkflowTask(
                task_id="robustness",
                name="Walk-Forward & Sensitivity Robustness",
                task_type="RobustnessTask",
                depends_on=["risk_analysis", "research_evaluation"],
            ),
            WorkflowTask(
                task_id="report_generation",
                name="Research Report Compilation",
                task_type="ReportGenerationTask",
                depends_on=["robustness"],
            ),
        ]

        # Validate DAG
        DAGValidator.validate_and_sort(tasks)

        config = {
            "dataset_id": "DS-SP500_DAILY-v1.0.0",
            "model_type": "xgboost",
            "slippage_bps": 5.0,
            "fee_bps": 10.0,
            "min_observations": 252,
            "data_observations": 1260,
            "max_leverage": 2.0,
            "leverage": 1.0,
        }
        if custom_config:
            config.update(custom_config)

        return Workflow(
            workflow_id=workflow_id,
            name=name,
            objective=objective,
            experiment_template="full_research",
            status=WorkflowStatus.READY,
            priority=Priority.NORMAL,
            tasks=tasks,
            resource_budget=resource_budget or ResourceBudget(),
            configuration=config,
        )

    @staticmethod
    def load_from_yaml(filepath: str) -> Workflow:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Workflow template file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        raw_tasks = data.get("tasks", [])
        tasks = []
        for t in raw_tasks:
            tasks.append(
                WorkflowTask(
                    task_id=t["task_id"],
                    name=t.get("name", t["task_id"]),
                    task_type=t["task_type"],
                    depends_on=t.get("depends_on", []),
                    configuration=t.get("configuration", {}),
                )
            )

        DAGValidator.validate_and_sort(tasks)

        return Workflow(
            workflow_id=f"WF-{uuid.uuid4().hex[:8].upper()}",
            name=data.get("name", "YAML Workflow"),
            objective=data.get("objective", "Workflow built from YAML"),
            experiment_template=data.get("experiment_template", "custom"),
            status=WorkflowStatus.READY,
            priority=Priority(data.get("priority", "NORMAL")),
            tasks=tasks,
            resource_budget=ResourceBudget(**data.get("resource_budget", {})),
            configuration=data.get("configuration", {}),
        )
