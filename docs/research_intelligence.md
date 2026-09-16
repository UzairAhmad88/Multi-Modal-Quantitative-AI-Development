# Phase 11: Research Intelligence, Experiment Automation & Quant Assistant Architecture

## Overview
Phase 11 introduces an institutional **Research Intelligence Layer** on top of the Multi-Modal Quant AI platform. It connects hypothesis formulation, experiment pre-registration, automated execution pipelines, multi-dimensional differential comparisons, feature ablations, robustness stress tests, confidence calibration, failure memory logging, evidence-based report generation, and interactive quantitative decision support.

```
DATA → FEATURES → MODELS → EXPERIMENTS → BACKTESTS → RISK → PAPER TRADING → RESULTS → DIAGNOSTICS → RESEARCH INSIGHTS
```

## System Core Rules
1. **RESEARCH-FIRST**: Designed strictly to systematically evaluate hypotheses and model improvements.
2. **PAPER-TRADING & BACKTEST ONLY**: Real-money live trading remains explicitly **DISABLED**.
3. **HUMAN-APPROVED**: Every experiment configuration requires explicit approval prior to execution.
4. **REPRODUCIBLE**: Experiments record seeds, version hashes, environment snapshots, and datasets.
5. **EVIDENCE-BASED LANGUAGE**: Research statements use non-promotional terms (`observed`, `measured`, `associated`, `consistent with`, `inconclusive`). Prohibited promotional claims (`guaranteed return`, `risk-free`) trigger automated validation blocks.

---

## Architecture Components

### 1. Hypothesis Management (`research_intelligence/hypothesis/`)
- Fields: `hypothesis_id`, `title`, `description`, `research_question`, `expected_effect`, `null_hypothesis`, `variables`, `dataset`, `time_period`, `status`, `created_at`.
- Lifecycle States: `DRAFT`, `REGISTERED`, `RUNNING`, `COMPLETED`, `REJECTED`, `SUPPORTED`, `INCONCLUSIVE`.
- Pre-Registration Specification: Objective, dataset, features, model, evaluation metrics, period, expected relationship defined prior to experimentation to minimize post-hoc bias.

### 2. Experiment Manager & Priority Queue (`research_intelligence/experiment_manager/`)
- Standardized Experiment Config: JSON/YAML specification with version tracking (`code_version`, `dataset_version`, `feature_version`, `model_version`, `config_version`).
- Unique Identifiers: `EXP-2026-000001` format.
- Priority Queue: `LOW`, `NORMAL`, `HIGH` execution sorting.
- Resource Limits: `max_cpu`, `max_memory_gb`, `max_parallel_jobs`, `max_training_time_sec`.
- Diagnostics Record: Captures `error_type`, `error_message`, `stack_trace`, `stage`, `timestamp`, and `environment` on failure.

### 3. Automated Experiment Runner (`research_intelligence/experiment_runner/`)
- Stage Pipeline: `CONFIG` → `DATA` → `FEATURES` → `TRAIN` → `VALIDATE` → `BACKTEST` → `RISK` → `ANALYSIS` → `REPORT`.
- Deduplication Engine: Searches historical memory; if identical dataset, features, model, and seed exist, reuses verified result unless forced.

### 4. Experiment Generator & Batch Runner (`research_intelligence/experiment_generator/`)
- Matrix Generation: Controlled single-variable pair creation (Treatment vs Control).
- Hyperparameter Search: Grid and Random Search over lookback, learning rate, hidden size, dropout, and threshold within resource bounds.

### 5. Multi-Metric Comparison Engine (`research_intelligence/comparison/`)
- Performs side-by-side differential analysis across dataset, features, model, CAGR, Sharpe, Sortino, max drawdown, turnover, costs, and accuracy.
- **No Single Composite Score**: Maintains multi-dimensional independence to prevent over-simplification.

### 6. Automated Feature Ablation Engine (`research_intelligence/ablation/`)
- Evaluates modality incremental value: `FULL`, `FULL_MINUS_NEWS`, `FULL_MINUS_FUNDAMENTALS`, `FULL_MINUS_REGIME`, `MARKET_ONLY`.

### 7. Robustness Stress Laboratory (`research_intelligence/robustness/`)
- Multi-dimensional parameter stress: Transaction cost sweeps (1 to 20 bps), period breakdown, threshold sensitivity, and stability metrics.

### 8. Diagnostics & Error Analyzer (`research_intelligence/diagnostics/`)
- Confidence Calibration (`ConfidenceCalibrator`): Measures Expected Calibration Error (ECE).
- Breakdown: False positives/negatives, market regime errors, news sentiment errors, and permutation feature importance.

### 9. Research Memory & Knowledge Store (`research_intelligence/research_memory/`)
- Stores verified `ResearchFinding` items, failure logs, and multi-node research graph lineage (`Hypothesis` → `Experiment` → `Finding`).

### 10. Research Recommendation Engine (`research_intelligence/recommendation_engine/`)
- Generates automated quantitative research directions (e.g., ablation suggestions, cost sensitivity tests, model architecture comparisons).

### 11. Report Generator (`research_intelligence/report_generator/`)
- Auto-generates structured Markdown reports into `reports/research/`.

---

## CLI Usage Guide

```bash
# Register hypothesis
python scripts/research_intel.py hypothesis create --title "VIX Regime Filter" --dataset market_sp500

# Create experiment
python scripts/research_intel.py experiment create --name EXP_LSTM_VIX --hypo-id HYP-2026-001

# List experiments
python scripts/research_intel.py experiment list

# Run experiment
python scripts/research_intel.py experiment run --id EXP-2026-000001

# Compare experiments
python scripts/research_intel.py experiment compare --ids EXP-2026-000001 EXP-2026-000002

# Reproduce experiment
python scripts/reproduce.py --experiment-id EXP-2026-000001

# Feature ablation
python scripts/research_intel.py ablation --experiment-id EXP-2026-000001

# Robustness stress test
python scripts/research_intel.py robustness --experiment-id EXP-2026-000001

# Error diagnostics
python scripts/research_intel.py analyze --experiment-id EXP-2026-000001

# Generate Markdown report
python scripts/research_intel.py report --experiment-id EXP-2026-000001
```

---

## REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/research/overview` | Platform research metrics overview |
| `GET` | `/research/hypotheses` | List registered hypotheses |
| `POST` | `/research/hypotheses` | Pre-register new hypothesis |
| `GET` | `/research/experiments` | List experiments |
| `POST` | `/research/experiments` | Create experiment config |
| `GET` | `/research/experiments/{id}` | Get experiment details |
| `POST` | `/research/experiments/{id}/run` | Execute experiment pipeline |
| `POST` | `/research/experiments/compare` | Differential comparison |
| `GET` | `/research/findings` | List verified research findings |
| `GET` | `/research/recommendations` | Get AI research suggestions |
| `GET` | `/research/graph` | Retrieve node-edge lineage graph |
