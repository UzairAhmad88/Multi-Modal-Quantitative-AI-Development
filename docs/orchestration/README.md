# Automated Research Pipeline & Experiment Orchestration (Phase 14)

## Architecture Overview

The Orchestration layer connects all quantitative AI research components—data loaders, feature engineering, NLP sentiment, AI model training, signal generation, portfolio optimization, backtesting, validation, robustness analysis, and reporting—into a single **automated, reproducible research workflow**.

```text
                 RESEARCH HYPOTHESIS
                         │
                         ▼
                  EXPERIMENT CONFIG
                         │
                         ▼
                    DATA LOAD
                         │
                         ▼
                  DATA VALIDATION
                         │
                         ▼
                  FEATURE ENGINE
                         │
                         ▼
                 TEMPORAL SPLIT
                         │
                         ▼
                    MODEL TRAIN
                         │
                         ▼
                   PREDICTION
                         │
                         ▼
                  SIGNAL ENGINE
                         │
                         ▼
                PORTFOLIO ENGINE
                         │
                         ▼
                     BACKTEST
                         │
                         ▼
                    VALIDATION
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      STATISTICS     ROBUSTNESS      STRESS
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  RESEARCH ANALYSIS
                         │
                         ▼
                  RESEARCH FINDING
                         │
                         ▼
                       REPORT
                         │
                         ▼
                  ARTIFACT REGISTRY
```

---

## 17-Stage Quantitative Research Pipeline

1. **CONFIGURATION**: Validate and lock experiment configuration parameters and random seeds.
2. **DATA**: Load market, news, and fundamental datasets.
3. **DATA_VALIDATION**: Execute data quality checks and freshness assertions.
4. **FEATURE_ENGINEERING**: Generate technical indicators, NLP sentiment, and fundamental metrics.
5. **DATASET_SPLIT**: Enforce strict temporal train/validation/test splits preventing lookahead bias.
6. **MODEL_TRAINING**: Fit ML/DL models (Multimodal, LSTM, Transformer, XGBoost).
7. **PREDICTION**: Generate multi-horizon return forecasts and win probabilities.
8. **SIGNAL_GENERATION**: Convert forecasts into normalized alpha signals.
9. **PORTFOLIO_CONSTRUCTION**: Compute optimized asset weights subject to position and risk limits.
10. **BACKTEST**: Execute event-driven historical simulation with transaction costs and slippage.
11. **VALIDATION**: Execute walk-forward and leakage detection gates.
12. **ROBUSTNESS**: Evaluate parameter sensitivity and perturbation robustness.
13. **STRESS_TESTING**: Apply historical crisis scenarios (e.g., 2008 Crash, COVID Shock, Tech Sell-Off).
14. **STATISTICAL_ANALYSIS**: Compute t-stats, p-values, and multiple testing adjustments.
15. **RESEARCH_FINDING**: Formulate structured empirical research observations and limitations.
16. **REPORT**: Compile comprehensive Markdown & JSON research reports.
17. **ARTIFACT_REGISTRATION**: Register complete run manifest and checksum lineage in experiment registry.

---

## CLI Reference

### 1. Run Experiment
```bash
python research/run_experiment.py --config configs/experiments/example.yaml
```

### 2. List Experiments
```bash
python research/list_experiments.py --model multimodal --status COMPLETED
```

### 3. Show Experiment Details
```bash
python research/show_experiment.py --id EXP-20260916-0001
```

### 4. Compare Experiments
```bash
python research/compare.py RUN-20260916-0001 RUN-20260916-0002
```

### 5. Reproduce Experiment
```bash
python research/reproduce.py --run-id RUN-20260916-0001
```

### 6. Cancel Run
```bash
python research/cancel.py --run-id RUN-20260916-0001
```

### 7. Resume Run from Checkpoint
```bash
python research/resume.py --run-id RUN-20260916-0001
```

---

## REST API Endpoints

- `GET /research/experiments`
- `POST /research/experiments`
- `GET /research/experiments/{id}`
- `POST /research/experiments/{id}/run`
- `POST /research/runs/{id}/resume`
- `POST /research/runs/{id}/cancel`
- `GET /research/runs/{id}`
- `GET /research/runs/{id}/logs`
- `GET /research/runs/{id}/artifacts`
- `POST /research/compare`
- `POST /research/reproduce`

---

## Safety & Governance Standards

- **NO LIVE TRADING**: Real-money trade execution is permanently disabled.
- **DETERMINISTIC SEEDS**: Random seeds for Python, NumPy, Scikit-Learn, and PyTorch are recorded and set.
- **CHECKPOINTING & RESUME**: JSON stage checkpoints enable zero-recomputation error recovery.
- **IMMUTABLE RUN RECORDS**: Completed experiment run records cannot be altered or overwritten.
