# Phase 22: Automated Quant Research Orchestrator OS

The **Automated Quant Research Orchestrator** transforms manual execution of quantitative research modules into controlled, observable, reproducible pipeline workflows. It coordinates existing engines (`data_platform/`, `model_factory/`, `portfolio_optimization/`, `execution/`, `backtests/`, `research_evaluation/`, `research_lab/`) without duplicating logic.

## Key Features

1. **DAG Workflow Builder & Topological Validator (`orchestrator/dependencies/`)**:
   - Validates task dependency graphs, checks for missing dependencies, and prevents execution loops via cycle detection (Kahn's algorithm).

2. **Standardized Task Contracts (`orchestrator/tasks/`)**:
   - `DataValidationTask`, `FeatureEngineeringTask`, `ModelTrainingTask`, `SignalGenerationTask`, `PortfolioConstructionTask`, `ExecutionSimulationTask`, `BacktestTask`, `RiskAnalysisTask`, `ResearchEvaluationTask`, `RobustnessTask`, `ReportGenerationTask`.

3. **Experiment Matrix Planner (`orchestrator/planner/`)**:
   - Converts high-level research plans into executable experiment matrices ($\text{Model} \times \text{Modality} \times \text{Strategy} \times \text{Execution}$) respecting explicit resource budgets.

4. **Validation Gates & Policy Engine (`orchestrator/gates/`, `orchestrator/policies/`)**:
   - Pre-task execution gates (`DataGate`, `LeakageGate`, `FeatureGate`, `ModelGate`, `BacktestGate`, `RiskGate`, `EvaluationGate`) and research safety policies enforcing test-set protection.

5. **Local Priority Queue & Subprocess Job Executor (`orchestrator/scheduler/`, `orchestrator/executor/`)**:
   - Managed priority queue (`LOW`, `NORMAL`, `HIGH`) and local execution with standard output/error log redirection.

6. **State Checkpointing & Workflow Resume (`orchestrator/state/`)**:
   - Persists completed task checkpoints, enabling workflow resume without re-running safe stages.

7. **Research Campaign Manager (`orchestrator/campaigns/`)**:
   - Groups related workflows into campaigns, tracking progress across experiment trees and compiling aggregate campaign markdown reports.

8. **CLI Tools (`orchestrator/cli/`)**:
   - `create.py`, `validate.py`, `start.py`, `status.py`, `pause.py`, `resume.py`, `cancel.py`, `retry.py`, `health.py`.

9. **REST API & Dashboard Page**:
   - Registered endpoints at `/orchestrator/workflows`, `/orchestrator/plans`, `/orchestrator/experiments/generate`, `/orchestrator/campaigns`, `/orchestrator/health`.
   - **29th Streamlit Workspace Page**: `dashboard/pages/29_Automated_Research_Orchestrator_OS.py`.

## Quick Start CLI Usage

```bash
# Create a new full research workflow
python orchestrator/cli/create.py --template full_research --name "Multimodal Research Pipeline"

# Validate workflow DAG and policy rules
python orchestrator/cli/validate.py --workflow WF-001

# Execute workflow
python orchestrator/cli/start.py --workflow WF-001

# Check workflow status and progress
python orchestrator/cli/status.py --workflow WF-001

# Inspect orchestrator health status
python orchestrator/cli/health.py
```
