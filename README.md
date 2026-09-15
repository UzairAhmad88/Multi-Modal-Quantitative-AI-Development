# Multi-Modal Quant AI

Advanced quantitative research capstone combining market data, financial news, NLP sentiment, fundamentals, machine learning, deep learning, alpha generation, portfolio construction, risk management, backtesting, and an interactive research dashboard.

## Core Pipeline

```text
Market Data ────────┐
                    ├──> Feature Engineering ──> Multi-Modal Fusion
News ───────────────┤                                  │
                    │                                  ▼
Fundamentals ───────┘                           ML + DL Models
                                                       │
                                                       ▼
                                                  Alpha Engine
                                                       │
                                                       ▼
                                               Portfolio Engine
                                                       │
                                                       ▼
                                                   Risk Engine
                                                       │
                                                       ▼
                                                  Backtester
                                                       │
                                                       ▼
                                              Quant Dashboard
```

## Objectives

- Build reproducible financial data pipelines.
- Engineer technical, sentiment, and fundamental features.
- Compare classical ML with LSTM, GRU, and Transformer models.
- Fuse multiple information modalities.
- Convert predictions into alpha scores and signals.
- Construct constrained portfolios.
- Apply portfolio risk controls.
- Backtest with transaction costs and slippage.
- Perform ablation, walk-forward, sensitivity, regime, and error analysis.
- Present research results in a clean interactive dashboard.

## Development Order

```text
Foundation
→ Market Data
→ Technical Features
→ News
→ NLP
→ Fundamentals
→ Fusion
→ ML
→ LSTM/GRU
→ Transformer
→ Multi-Modal Model
→ Alpha
→ Portfolio
→ Risk
→ Backtesting
→ Dashboard
→ Testing
→ Research Validation
→ Final Documentation
```

Do not start with the Transformer. Establish correct data and baseline behavior first.

## Repository

```text
multi_modal_quant_ai/
├── configs/                 Configuration
├── data/                    Raw and processed datasets
├── notebooks/               Research notebooks
├── src/
│   ├── data/                Data ingestion and synchronization
│   ├── features/            Feature engineering
│   ├── nlp/                 Financial NLP
│   ├── models/              ML and DL
│   ├── alpha/               Alpha and signals
│   ├── portfolio/           Allocation
│   ├── risk/                Risk controls
│   ├── backtesting/         Historical simulation
│   ├── evaluation/          Metrics and comparisons
│   └── utils/               Shared utilities
├── models/                  Model artifacts
├── experiments/             Experiment outputs
├── backtests/               Backtest outputs
├── dashboard/               Streamlit UI
├── tests/                   Tests
├── scripts/                 CLI scripts
└── logs/                    Runtime logs
```

## Local Setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Configure:

```bash
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Run tests:

```bash
pytest
```

Launch dashboard:

```bash
streamlit run dashboard/app.py
```

## Data Leakage Policy

Financial data must be aligned using information availability. Never allow a future observation to influence a historical prediction.

Preserve:

- observation timestamp
- publication timestamp
- effective/availability timestamp
- ingestion timestamp where relevant

Fundamental data must become available only after its actual public release. News must be aligned by publication time.

## Evaluation

Never randomly shuffle time-series data.

Use chronological splits and, for advanced validation, walk-forward testing.

Required comparisons:

```text
Market only
Market + News
Market + Fundamentals
Market + News + Fundamentals
```

Required model comparison:

```text
Logistic Regression
Random Forest
XGBoost
LSTM
GRU
Transformer
Multi-Modal Ensemble
```

## Risk and Backtesting

Backtests must include:

- execution timing
- transaction costs
- slippage
- turnover
- cash
- position limits
- rebalancing

Required metrics:

- total return
- annualized return
- annualized volatility
- Sharpe
- Sortino
- maximum drawdown
- Calmar
- win rate
- profit factor
- turnover
- trade count

## Dashboard

The dashboard should be clean, soft, professional, minimal, and research-oriented.

Pages:

- Overview
- Market
- News & Sentiment
- Fundamentals
- AI Predictions
- Alpha Signals
- Portfolio
- Risk
- Backtesting
- Model Lab
- Experiments
- System

## Completion Criteria

The project is complete when all three modalities work, leakage controls are verified, ML/DL models train, multi-modal fusion works, alpha signals are generated, portfolios obey risk constraints, realistic backtests run, walk-forward validation is available, ablation results are documented, dashboard outputs are connected, tests pass, and documentation is complete.

## Disclaimer

This repository is for education and quantitative research. Historical backtests can be misleading because of overfitting, leakage, survivorship bias, data quality, market regime changes, transaction costs, slippage, and model drift. Nothing here guarantees future investment performance.
