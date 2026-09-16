"""
Unit Tests for Phase 22 Automated Quant Research Orchestrator.
"""

import os
import pytest
from orchestrator.core.orchestrator import ResearchOrchestrator
from orchestrator.schemas.workflow_schema import WorkflowTask, ResearchPlan
from orchestrator.dependencies.dag_validator import DAGValidator, DAGValidationError
from orchestrator.planner.experiment_planner import ExperimentPlanner
from orchestrator.policies.policy_engine import ResearchPolicyEngine
from orchestrator.resources.resource_monitor import ResourceMonitor
from orchestrator.campaigns.campaign_manager import CampaignManager


def test_dag_cycle_detection():
    # Intentionally cyclic graph: A -> B -> C -> A
    tasks = [
        WorkflowTask(task_id="A", name="Task A", task_type="DataValidationTask", depends_on=["C"]),
        WorkflowTask(task_id="B", name="Task B", task_type="FeatureEngineeringTask", depends_on=["A"]),
        WorkflowTask(task_id="C", name="Task C", task_type="ModelTrainingTask", depends_on=["B"]),
    ]
    with pytest.raises(DAGValidationError):
        DAGValidator.validate_and_sort(tasks)


def test_dag_missing_dependency():
    tasks = [
        WorkflowTask(task_id="A", name="Task A", task_type="DataValidationTask", depends_on=["MISSING_TASK"]),
    ]
    with pytest.raises(DAGValidationError):
        DAGValidator.validate_and_sort(tasks)


def test_workflow_creation_and_execution():
    orchestrator = ResearchOrchestrator(storage_dir="artifacts/test_workflows")
    wf = orchestrator.create_workflow(name="Test Research Pipeline", template="full_research")
    assert wf.workflow_id.startswith("WF-")

    validated_policies = orchestrator.validate_workflow(wf.workflow_id)
    assert len(validated_policies) >= 7

    res_wf = orchestrator.start_workflow(wf.workflow_id)
    assert res_wf.status == "COMPLETED"
    assert len(res_wf.completed_tasks) == len(res_wf.tasks)

    events = orchestrator.get_events(wf.workflow_id)
    assert len(events) >= 5


def test_experiment_planner_matrix():
    plan = ResearchPlan(
        plan_id="PLAN-TEST",
        name="Test Plan",
        objective="Test matrix generation",
        hypothesis="Multi-modal alpha hypothesis",
        dataset_id="DS-SP500",
        models=["xgboost", "lstm"],
        modalities=["market", "all"],
        strategies=["long_short"],
        executions=["twap"],
    )
    plan.resource_budget.max_experiments = 3
    matrix = ExperimentPlanner.generate_matrix(plan)
    assert len(matrix) == 3
    assert matrix[0].experiment_id.startswith("EXP-")


def test_policy_engine_verification():
    policy_engine = ResearchPolicyEngine()
    context = {
        "dataset_id": "DS-TEST",
        "has_future_labels": False,
        "features": ["f1", "f2"],
        "model_type": "xgboost",
        "slippage_bps": 5.0,
        "fee_bps": 10.0,
        "min_observations": 100,
        "data_observations": 500,
        "max_leverage": 2.0,
        "leverage": 1.0,
    }
    results = policy_engine.evaluate_all(context)
    failures = [r for r in results if r.status == "FAIL"]
    assert len(failures) == 0


def test_policy_engine_leakage_rejection():
    policy_engine = ResearchPolicyEngine()
    context = {
        "dataset_id": "DS-TEST",
        "has_future_labels": True,  # Leakage injected
    }
    results = policy_engine.evaluate_all(context)
    failures = [r for r in results if r.status == "FAIL"]
    assert len(failures) >= 1
    assert any(f.policy == "LeakageGate" for f in failures)


def test_resource_monitor():
    metrics = ResourceMonitor.get_current_metrics()
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "memory_used_gb" in metrics


def test_campaign_manager():
    cm = CampaignManager(storage_dir="artifacts/test_campaigns")
    plan = ResearchPlan(
        plan_id="PLAN-CMP",
        name="Campaign Plan",
        objective="Test campaign objective",
        hypothesis="Hypothesis statement",
        dataset_id="DS-SP500",
        models=["xgboost"],
        modalities=["market"],
    )
    c = cm.create_campaign(name="Alpha Campaign", objective="Test objective", plan=plan)
    assert c.campaign_id.startswith("CMP-")
    assert len(c.experiments) >= 1

    report = cm.build_campaign_report(c.campaign_id)
    assert "# Research Campaign Report" in report
