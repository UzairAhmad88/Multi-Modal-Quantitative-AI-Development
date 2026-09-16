# Phase 21: Quantitative Research Laboratory OS

## Overview

Phase 21 transforms the Multi-Modal Quant AI platform into a systematic quantitative research laboratory. It introduces hypothesis-driven experiment creation, lifecycle tracking (`DRAFT`, `READY`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `ARCHIVED`), immutable configuration snapshots & SHA256 hashing, dataset/feature/model/strategy/portfolio/execution/evaluation snapshots, metric logging, artifact indexing, research lineage DAG graphs (`LineageGraph`), experiment comparison & diff engines, research knowledge base & findings indexing, research intelligence, replication & reproducibility checks (`ReplicationExperiment`), CLI tools, REST API routes, and an interactive Streamlit UI workspace page.

## Key Modules

### 1. Experiment Lifecycle & Schemas (`research_lab/experiments/`, `research_lab/schemas/`, `research_lab/runs/`)
- `ExperimentStatus`: Lifecycle enum (`DRAFT`, `READY`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `ARCHIVED`).
- `Experiment`: Standardized dataclass schema with deterministic `compute_config_hash()`.
- `ExperimentRun`: Execution run tracking status, seed, host metadata, runtime duration, metrics, and artifact links.

### 2. Hypothesis & Knowledge Base (`research_lab/hypotheses/`, `research_lab/knowledge_base/`)
- `HypothesisManager`: Manages research questions, hypotheses, expected behavior, and null hypotheses.
- `Finding`: Structured record of research discoveries, supporting evidence, confidence levels, and limitations.
- `ResearchKnowledgeBase`: Indexes findings, notes, failed experiment lessons, and keyword search.

### 3. Lineage Graph & Tracking (`research_lab/lineage/`, `research_lab/tracking/`, `research_lab/artifacts/`)
- `LineageGraph`: Maps end-to-end DAG: Dataset -> Feature -> Model -> Signal -> Portfolio -> Execution -> Backtest -> Evaluation -> Experiment -> Report.
- `MetricStore`: Logs prediction, portfolio, risk, execution, and statistical metrics per run.
- `ArtifactStore`: Indexes data files, models, plots, logs, and reports with content hashing.

### 4. Comparison, Intelligence & Reproducibility (`research_lab/comparison/`, `research_lab/intelligence/`, `research_lab/reproducibility/`)
- `ExperimentComparisonEngine`: Side-by-side metric comparison with fairness comparability checks.
- `ExperimentDiff`: Key-by-key configuration diff analysis.
- `ResearchIntelligenceEngine`: Synthesizes research insights and discovers cross-experiment patterns.
- `ReproducibilityChecker` & `ReplicationExperiment`: Verifies exact replication runs (`MATCH`, `PARTIAL_MATCH`, `MISMATCH`).

### 5. Experiment Reports (`research_lab/reports/`)
- `ExperimentReportBuilder`: Generates structured Markdown, HTML, and JSON reports.

## Usage

### CLI Tools
```bash
# Create experiment from template
python research_lab/cli/create.py --template multimodal --name "Fusion Experiment"

# Run experiment
python research_lab/cli/run.py --experiment EXP-001

# Compare experiments
python research_lab/cli/compare.py --experiments EXP-001,EXP-002

# Replicate experiment
python research_lab/cli/replicate.py --experiment EXP-001

# Export experiment report
python research_lab/cli/report.py --experiment EXP-001 --format html
```

### REST API
- `POST /research-lab/experiments`
- `GET /research-lab/experiments`
- `GET /research-lab/experiments/{id}`
- `PUT /research-lab/experiments/{id}`
- `POST /research-lab/experiments/{id}/run`
- `POST /research-lab/experiments/{id}/clone`
- `POST /research-lab/experiments/{id}/replicate`
- `GET /research-lab/experiments/{id}/lineage`
- `GET /research-lab/experiments/{id}/metrics`
- `GET /research-lab/experiments/{id}/artifacts`
- `POST /research-lab/compare`
- `GET /research-lab/reports/{id}`

### Streamlit Workspace Page
- **Page 28**: `dashboard/pages/28_Research_Laboratory_OS.py`
