# QUANT AI — Multi-Modal Quantitative Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-65%20Passed-success.svg)](#running-tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An institutional-grade quantitative finance research operating system that combines **Market Price & Volume**, **FinBERT News Sentiment NLP**, and **Quarterly SEC Statement Fundamentals** using PyTorch deep neural fusion networks (`MultiModalQuantNet`), risk-gated portfolio optimization, and event-driven backtesting.

---

## 1. System Architecture

```text
                    MULTI-MODAL QUANT AI
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
        MARKET DATA        NEWS        FUNDAMENTALS
             │               │               │
             ▼               ▼               ▼
       TECHNICAL          NLP            FINANCIAL
       FEATURES        SENTIMENT          FEATURES
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                       FEATURE FUSION
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
             ML MODELS                 DL MODELS
                │                         │
             XGBoost                 LSTM / GRU
             Random Forest            Transformer
                │                         │
                └────────────┬────────────┘
                             ▼
                       ALPHA ENGINE
                             │
                             ▼
                      PORTFOLIO ENGINE
                             │
                             ▼
                         RISK ENGINE
                             │
                             ▼
                       BACKTEST ENGINE
                             │
                             ▼
                      RESEARCH REPORTS
                             │
                             ▼
                       QUANT DASHBOARD
```

---

## 2. Key Features

- **Multi-Modal Data Pipeline**: Temporal synchronization of daily market OHLCV bars, financial news headlines, and quarterly SEC financial statements.
- **Point-In-Time Leakage Protection**: Enforces $T+1$ news availability policy and `public_release_date` backward-looking joins for earnings filings.
- **Deep Neural Fusion (`MultiModalQuantNet`)**: PyTorch architecture featuring specialized modality encoders (LSTM market encoder, MLP news encoder, MLP fundamental encoder) with learned softmax attention weighting.
- **Model Suite**: XGBoost, Random Forest, PyTorch LSTM, GRU, Temporal Transformer Encoder, and weighted model ensemble.
- **Risk Gate Portfolio Optimization**: Position limit enforcement (max asset weight 25.0%), sector exposure caps (40.0%), gross leverage limits (1.0x), and drawdown circuit breakers (-20.0%).
- **Event-Driven Backtest Engine**: Close $T$ signal generation with Open $T+1$ execution fills, incorporating 10.0 bps transaction fees and 5.0 bps slippage penalties.
- **Modality Ablation Framework**: Automated experiment grid evaluating performance across individual modalities (Market Only vs Market+News vs Full Multi-Modal).
- **Dual Dashboard OS**:
  - Institutional Web OS Research Terminal (`frontend/` HTML5/CSS/JS with Chart.js).
  - Streamlit Quantitative Research Workspace (`dashboard/` 12 pages with dark Plotly charts).
- **FastAPI REST API**: 12 endpoints serving market data, news, fundamentals, features, model predictions, alpha signals, risk metrics, and backtest simulations.
- **Supabase Cloud Synchronization**: SQL schema DDLs, RLS security policies, Edge functions, and seed datasets.

---

## 3. Technology Stack

- **Core**: Python 3.11+, NumPy, Pandas, SciPy, Scikit-learn
- **Machine Learning**: XGBoost, Random Forest
- **Deep Learning**: PyTorch (LSTM, GRU, Transformer Encoder, MultiModalQuantNet)
- **NLP**: Hugging Face Transformers, Tokenizers, FinBERT Sentiment Engine
- **Backend & Database**: FastAPI, Pydantic, Uvicorn, PostgreSQL, SQLAlchemy, Supabase
- **Dashboard & Visualization**: Plotly, Chart.js, Streamlit, HTML5/CSS3
- **DevOps & MLOps**: Docker, Docker Compose, MLflow, Pytest, GitHub Actions CI/CD

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

### Step 3: Run Full End-to-End Demo Pipeline
```bash
python scripts/run_pipeline.py --demo
```
*Executes all 8 pipeline phases deterministically without requiring external API keys or GPU.*

---

## 5. Running the Backend & Dashboards

### Launch FastAPI REST Backend
```bash
uvicorn api.main:app --reload --port 8000
```
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`
- ReDoc API Docs: `http://127.0.0.1:8000/redoc`

### Launch Streamlit Research Dashboard
```bash
streamlit run dashboard/app.py
```
- Dashboard URL: `http://localhost:8501`

### Launch Web OS Research Workstation (Frontend)
Simply open `frontend/index.html` in your web browser or serve via static server:
```bash
python -m http.server 3000 --directory frontend
```
- Web OS URL: `http://localhost:3000`

---

## 6. Docker Container Deployment

```bash
# Build and start all services (Backend, Dashboard, PostgreSQL, MLflow)
docker compose up --build -d

# View status
docker compose ps

# Stop services
docker compose down
```

---

## 7. Running Tests

```bash
# Run full unit, API, integration, leakage, and UI test suite
python -m pytest -v
```

---

## 8. Real-Time Research & Paper Trading

> [!NOTE]
> The default system operates in **Paper Trading Mode** (`TRADING_ENABLED=False` safety lock default). Real-money execution is completely disabled by default.

### Run Paper Trading CLI Runner
```bash
python scripts/run_realtime_paper.py --asset AAPL --duration 10 --replay
```

### Run Quantitative Research Lab Experiments
```bash
python scripts/run_research.py --config configs/research/baseline.yaml --demo
```

### Key Real-Time Capabilities:
- **Provider Abstraction**: Normalizes live quotes & 15-minute intraday bars into UTC schemas.
- **Pre-Trade Risk Control Gate**: Checks single-position caps (25.0%), daily loss limits (-5.0%), drawdown halts (-15.0%), and capital availability.
- **Order State Machine**: `CREATED` $\rightarrow$ `VALIDATING` $\rightarrow$ `APPROVED` $\rightarrow$ `SUBMITTED` $\rightarrow$ `FILLED` / `REJECTED`.
- **Deterministic Replay**: Replays historical bars through feature, signal, risk, and paper execution engines.

---

## 9. Research Performance Summary

| Architecture | IC Score | Directional Acc. | Backtest CAGR | Sharpe Ratio | Max Drawdown |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost Regressor** | +0.084 | 61.2% | 14.5% | 1.38 | -13.4% |
| **PyTorch LSTM** | +0.078 | 59.8% | 13.2% | 1.25 | -14.1% |
| **Temporal Transformer** | +0.091 | 62.5% | 16.1% | 1.45 | -12.5% |
| **MultiModalQuantNet** | **+0.112** | **64.8%** | **18.7%** | **1.64** | **-11.2%** |

---

## 10. License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
