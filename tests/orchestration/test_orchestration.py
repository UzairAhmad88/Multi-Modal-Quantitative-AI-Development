"""
Comprehensive Test Suite for Phase 14 - Automated Research Pipeline & Experiment Orchestration.
"""

import os
import shutil
import tempfile
import pytest
from pathlib import Path

from orchestration.dependency_graph import DependencyGraph, PipelineStage
from orchestration.state_manager import StateManager, PipelineState, StageState
from orchestration.checkpoint_manager import CheckpointManager
from orchestration.retry_manager import RetryManager
from orchestration.resource_manager import ResourceManager
from orchestration.artifact_manager import ArtifactManager
from orchestration.logging_manager import LoggingManager
from orchestration.job_queue import JobQueue, JobPriority
from orchestration.scheduler import ResearchScheduler
from orchestration.task_registry import TaskRegistry
from orchestration.executor import StageExecutor
from orchestration.pipeline import ResearchPipeline
from research.registry.registry import ExperimentRegistry


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_config():
    return {
        "experiment": {
            "name": "unit_test_experiment",
            "description": "Test experiment",
            "seed": 42
        },
        "data": {
            "symbols": ["AAPL"],
            "start": "2021-01-01",
            "end": "2023-01-01"
        },
        "features": {
            "market": True,
            "news": True,
            "fundamentals": True
        },
        "model": {
            "type": "multimodal",
            "version": "1.0"
        },
        "backtest": {
            "initial_capital": 100000.0,
            "transaction_cost": 0.001,
            "slippage": 0.0005
        },
        "validation": {
            "walk_forward": True,
            "leakage_detection": True,
            "bootstrap": True
        },
        "report": {
            "generate": True
        }
    }


def test_dependency_graph():
    stages = DependencyGraph.get_ordered_stages()
    assert len(stages) == 17
    assert stages[0] == PipelineStage.CONFIGURATION
    assert stages[-1] == PipelineStage.ARTIFACT_REGISTRATION

    deps_data_val = DependencyGraph.get_prerequisites(PipelineStage.DATA_VALIDATION)
    assert PipelineStage.DATA in deps_data_val


def test_state_manager():
    sm = StateManager()
    run_state = sm.create_run_state("RUN-001", "EXP-001")
    assert run_state.status == PipelineState.PENDING

    sm.start_pipeline("RUN-001")
    assert sm.get_run_state("RUN-001").status == PipelineState.RUNNING

    sm.start_stage("RUN-001", PipelineStage.DATA)
    sm.complete_stage("RUN-001", PipelineStage.DATA, duration=1.2)
    assert sm.get_run_state("RUN-001").stage_records[PipelineStage.DATA.value].status == StageState.COMPLETED

    sm.fail_stage("RUN-001", PipelineStage.MODEL_TRAINING, "Test Error")
    assert sm.get_run_state("RUN-001").status == PipelineState.FAILED


def test_checkpoint_and_resume(temp_dir):
    cm = CheckpointManager(base_artifact_dir=temp_dir)

    data_payload = {"symbols": ["AAPL"], "status": "LOADED"}
    cm.save_checkpoint("EXP-001", PipelineStage.DATA, data_payload)

    assert cm.has_checkpoint("EXP-001", PipelineStage.DATA)
    loaded = cm.load_checkpoint("EXP-001", PipelineStage.DATA)
    assert loaded == data_payload


def test_retry_manager():
    rm = RetryManager(enabled=True, max_attempts=3)
    assert rm.is_retryable(PipelineStage.DATA, Exception("network error"))
    assert not rm.is_retryable(PipelineStage.VALIDATION, Exception("validation failure"))


def test_resource_manager():
    rm = ResourceManager(max_memory_gb=100.0, max_runtime_minutes=60)
    usage = rm.get_resource_usage()
    assert "cpu_percent" in usage
    assert "memory_usage_gb" in usage
    rm.check_limits()


def test_job_queue():
    jq = JobQueue()
    job = jq.enqueue("RUN-001", "EXP-001", "configs/experiments/example.yaml", priority=JobPriority.HIGH)
    assert len(jq.list_jobs()) == 1
    next_job = jq.pop_next_job()
    assert next_job is not None
    assert next_job.job_id == "JOB-RUN-001"
    assert next_job.status == "RUNNING"


def test_experiment_registry(temp_dir):
    reg_file = str(Path(temp_dir) / "registry.json")
    reg = ExperimentRegistry(registry_file=reg_file)

    reg.register_experiment("EXP-TEST-01", "Test Exp", {"seed": 42}, tags=["test"])
    exp = reg.get_experiment("EXP-TEST-01")
    assert exp is not None
    assert exp["name"] == "Test Exp"

    reg.register_run("RUN-TEST-01", "EXP-TEST-01", {"seed": 42}, status="COMPLETED", metrics={"sharpe": 1.8})
    run = reg.get_run("RUN-TEST-01")
    assert run is not None
    assert run["metrics"]["sharpe"] == 1.8

    search = reg.list_experiments(status="COMPLETED")
    assert len(search) == 1
    assert search[0]["run_id"] == "RUN-TEST-01"


def test_full_research_pipeline_execution(sample_config):
    pipeline = ResearchPipeline(config=sample_config)
    run_record = pipeline.execute()

    assert run_record["status"] == "COMPLETED"
    assert run_record["completed_stages"] == 17
    assert "sharpe" in run_record["metrics"]
    assert run_record["metrics"]["sharpe"] > 0


def test_pipeline_resume_execution(sample_config, temp_dir):
    pipeline1 = ResearchPipeline(config=sample_config)
    run1 = pipeline1.execute()
    run_id = run1["run_id"]

    pipeline2 = ResearchPipeline(config=sample_config, resume_run_id=run_id)
    run2 = pipeline2.execute()

    assert run2["status"] == "COMPLETED"
    assert run2["run_id"] == run_id


def test_failure_injection(sample_config):
    sample_config["_inject_failure_stage"] = "MODEL_TRAINING"
    pipeline = ResearchPipeline(config=sample_config)
    run_record = pipeline.execute()

    assert run_record["status"] == "FAILED"
    assert run_record["failed_stage"] == "MODEL_TRAINING"
    assert "Injected failure" in run_record["error"]
