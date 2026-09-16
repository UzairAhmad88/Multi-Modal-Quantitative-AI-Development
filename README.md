# QUANT AI — Multi-Modal Quantitative Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-250%20Passed-success.svg)](#running-tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An institutional-grade quantitative finance research operating system that combines **Market Price & Volume**, **FinBERT News Sentiment NLP**, and **Quarterly SEC Statement Fundamentals** using PyTorch deep neural fusion networks (`MultiModalQuantNet`), risk-gated portfolio optimization, execution simulation & market microstructure OS, out-of-sample research evaluation & statistical validation OS, systematic research laboratory OS, automated research pipeline orchestration & DAG scheduling, research knowledge base & experiment intelligence OS, statistical validation & research integrity OS, MLOps model registry, pre-trade risk controls, real-time paper trading execution, and a **Quant Research Intelligence Engine**.

---

## 1. System Architecture

```text
                    QUANT DATA
                        │
                        ▼
                PATTERN DISCOVERY
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       MARKET          NEWS       FUNDAMENTALS
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                CROSS-MODAL ANALYSIS
                        │
                        ▼
                    ANOMALIES
                        │
                        ▼
                HYPOTHESIS ENGINE
                        │
                        ▼
              EXPERIMENT GENERATOR
                        │
                        ▼
              RESEARCH ORCHESTRATOR
                        │
                        ▼
                   VALIDATION
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      STATISTICS     ROBUSTNESS     STRESS
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  EVIDENCE ENGINE
                        │
                        ▼
                 RESEARCH FINDING
                        │
                        ▼
               FOLLOW-UP QUESTIONS
                        │
                        ▼
                RESEARCH KNOWLEDGE
```

---

## 2. Key Features

- **Portfolio Optimization, Position Sizing & Construction OS (Phase 18)**: Mathematical portfolio construction system (`MODEL` $\rightarrow$ `ALPHA SIGNAL` $\rightarrow$ `EXPECTED RETURN` $\rightarrow$ `RISK ESTIMATOR` $\rightarrow$ `OPTIMIZER` $\rightarrow$ `CONSTRAINTS` $\rightarrow$ `TRANSACTION COSTS` $\rightarrow$ `REBALANCING` $\rightarrow$ `RISK ATTRIBUTION`), Equal Weight, Inverse Volatility, Risk Parity, Mean-Variance (Markowitz), Minimum Variance, and Target Volatility allocators, `ConstraintEngine` (long-only, position bounds, gross exposure, turnover limits), `ExpectedReturnEstimator`, `CovarianceEstimator` (Ledoit-Wolf shrinkage & PSD eigenvalue clipping), `PositionSizingEngine` (Fractional Kelly, Volatility sizing), `TransactionCostEngine` (commission, spread, slippage), `RebalancingEngine`, `RiskAttributionEngine` (MCR, % risk contribution), `ScenarioEngine`, 4 CLI tools (`portfolio_optimization/cli/optimize.py`, etc.), REST API endpoints, and a 25-page Streamlit workspace (`/portfolio_opt`).
- **Quantitative Data Platform, PIT Store & Feature Store OS (Phase 17)**: End-to-end reproducible, versioned, and point-in-time correct data pipeline (`DATA SOURCES` $\rightarrow$ `RAW` $\rightarrow$ `NORMALIZATION` $\rightarrow$ `DATA QUALITY` $\rightarrow$ `PIT ALIGNMENT` $\rightarrow$ `FEATURE STORE` $\rightarrow$ `DATASET BUILDER` $\rightarrow$ `VERSIONED DATASET` $\rightarrow$ `MODEL FACTORY`), `DataSource` connectors, `RawDataStore`, `DataQualityEngine`, `PointInTimeManager` (preventing news and fundamental look-ahead leakage), `FeatureEngine`, `FeatureStoreRegistry` catalog, disk-backed `FeatureCache`, `DatasetBuilder` (`DATASET-YYYYMMDD-XXXX`), immutable `SnapshotManager`, `DataLineageTracer` DAG, 6 CLI tools (`data_platform/cli/ingest.py`, etc.), REST API endpoints, and a 24-page Streamlit workspace (`/data`).
- **Model Factory, Registry & Controlled Model Lifecycle OS (Phase 16)**: Standardized lifecycle management (`DATA` $\rightarrow$ `FEATURES` $\rightarrow$ `CONFIG` $\rightarrow$ `TRAIN` $\rightarrow$ `VALIDATE` $\rightarrow$ `BACKTEST` $\rightarrow$ `ROBUSTNESS` $\rightarrow$ `REGISTER` $\rightarrow$ `COMPARISON` $\rightarrow$ `CANDIDATE` $\rightarrow$ `PAPER TRADING` $\rightarrow$ `MONITORING` $\rightarrow$ `RETRAINING` $\rightarrow$ `ARCHIVE`), ModelFactory instantiator, YAML configurations, GPU detection with CPU safe fallback, early stopping, loss tracking, task-aware evaluation, model comparison engine, ablation, Voting/Averaging/Stacking/Blending ensemble engine, drift detectors, champion/challenger selection, automated gate promotion, rollback, 11 CLI tools (`models/train.py`, etc.), REST API endpoints, and a 23-page Streamlit workspace (`/models`).
- **Quant Research Intelligence & Pattern OS (Phase 15)**: Multi-modal pattern discovery, event studies, lead-lag analysis, anomaly detection, structured hypothesis generation, network research graph lineage, evidence classification, persistent memory, and evidence-based natural language research queries.
- **Automated Research Pipeline & Orchestration (Phase 14)**: 17-stage configuration-driven workflow with DAG dependency graph, JSON stage checkpointing, zero-recomputation resume, and reproducible experiment lineage.
- **Multi-Modal Data Pipeline**: Temporal synchronization of daily market OHLCV bars, financial news headlines, and quarterly SEC financial statements.
- **Point-In-Time Leakage Protection**: Enforces $T+1$ news availability policy and `public_release_date` backward-looking joins for earnings filings (`DataLeakageAuditor`).
- **Deep Neural Fusion (`MultiModalQuantNet`)**: PyTorch architecture featuring specialized modality encoders (LSTM market encoder, MLP news encoder, MLP fundamental encoder) with learned softmax attention weighting.
- **Model Suite**: XGBoost, Random Forest, PyTorch LSTM, GRU, Temporal Transformer Encoder, and weighted model ensemble.
- **Advanced Portfolio Construction**: Mean-Variance, Risk Parity, Hierarchical Risk Parity (HRP), Black-Litterman, and Ledoit-Wolf Shrinkage covariance optimization.
- **Pre-Trade Risk Gate & Kill Switch**: Position limit enforcement (max asset weight 25.0%), gross leverage limits (1.0x), drawdown circuit breakers (-10.0%), and `TradingKillSwitch`.
- **MLOps & Model Registry**: `ExperimentManager`, `DatasetRegistry` (SHA-256 manifests), `FeatureRegistry`, `ModelRegistry` (`EXPERIMENTAL` $\rightarrow$ `VALIDATED` $\rightarrow$ `PAPER` $\rightarrow$ `ARCHIVED`), and Lineage DAGs.
- **Real-Time Paper Trading & Replay**: Continuous paper-trading simulation with 5 bps slippage, 10 bps commission, and 100x accelerated historical market replay engine (`RealtimeReplayEngine`).
- **25-Page Quant Workspace**: Streamlit dashboard workspace (`dashboard/`) covering Overview, Market, News/NLP, Fundamentals, Predictions, Signals, Portfolio, Risk, Backtesting, Experiments, MLOps Registry, Paper Trading, Research Validation, Research Orchestration, Research Intelligence, Model Factory, Data Platform, and **Portfolio Optimization OS**.
- **FastAPI REST Backend**: REST API endpoints serving market data, news, fundamentals, features, predictions, signals, risk metrics, portfolio allocations, MLOps registry, paper trading controls, research orchestration, research intelligence, model factory, data platform, and portfolio optimization.


---

## 3. Technology Stack

- **Core**: Python 3.11+, NumPy, Pandas, SciPy, Scikit-learn
- **Machine Learning**: XGBoost, Random Forest
- **Deep Learning**: PyTorch (LSTM, GRU, Transformer Encoder, MultiModalQuantNet)
- **NLP**: Hugging Face Transformers, Tokenizers, FinBERT Sentiment Engine
- **Backend & Database**: FastAPI, Pydantic, Uvicorn, PostgreSQL, Supabase
- **Dashboard & Visualization**: Plotly, Streamlit, HTML5/CSS3
- **MLOps & Research**: Custom MLOps Package (`src/mlops/`), Dataset Manifests, Lineage DAGs, Pytest

---

## 4. Quick Start Guide

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/UzairAhmad88/Multi-Modal-Quantitative-AI-Development.git
cd Multi-Modal-Quantitative-AI-Development

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Run System Integrity Check & 13-Step End-to-End Demo
```bash
python scripts/system_check.py
python scripts/demo.py
```

---

## 5. Running the Backend & Dashboard

### Launch FastAPI REST Backend
```bash
uvicorn api.main:app --reload --port 8000
```
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

### Launch Streamlit Research Workspace (17 Pages)
```bash
streamlit run dashboard/app.py
```
- Dashboard URL: `http://localhost:8501`

---

## 6. Real-Time Paper Trading & Historical Replay

> [!IMPORTANT]
> **REAL-MONEY TRADING = DISABLED**  
> **LIVE BROKER ORDERS = DISABLED**  
> **PAPER TRADING ONLY (`TRADING_MODE=paper`)**

### Run Paper Trading Session
```bash
python scripts/realtime.py start --config configs/realtime/paper.yaml
```

### Run Accelerated Historical Market Data Replay
```bash
python scripts/realtime.py replay --config configs/realtime/replay.yaml
```

---

## 7. Running Tests

```bash
# Run full unit, API, integration, leakage, MLOps, and real-time test suite (120/120 passed)
python -m pytest -v
```

---

## 8. Research Performance & Benchmarking Summary

| Architecture | Directional Acc. | RMSE | CAGR | Sharpe Ratio | Max Drawdown |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Buy & Hold Benchmark** | 52.1% | 0.0185 | +12.40% | 0.85 | -15.40% |
| **Naive Random Forecast** | 50.0% | 0.0210 | +1.20% | 0.15 | -22.10% |
| **XGBoost Alpha Regressor** | 61.2% | 0.0131 | +15.40% | 1.45 | -10.20% |
| **PyTorch LSTM** | 62.8% | 0.0128 | +16.80% | 1.58 | -9.50% |
| **MultiModalQuantNet** | **65.4%** | **0.0118** | **+19.80%** | **1.84** | **-8.10%** |

---

## 9. License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
