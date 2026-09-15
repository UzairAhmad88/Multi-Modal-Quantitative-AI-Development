# Quantitative Methodology & System Architecture

## 1. System Architecture
The platform implements an end-to-end multi-modal quantitative pipeline:
```text
Market OHLCV + News Text NLP + Fundamental Ratios
          ↓
Temporal Asof Alignment (Lookahead-bias free)
          ↓
Feature Store & Sequence Builder
          ↓
XGBoost / LSTM / GRU / Transformer / Multi-Modal Network
          ↓
Model Ensemble & Alpha Engine
          ↓
Risk-Gated Portfolio Allocator
          ↓
Event-Driven Execution & Backtest Engine (10 bps fee, 5 bps slippage)
```

## 2. Temporal Alignment Rules (Lookahead Prevention)
- **Market Data**: Daily close $T$ available at close.
- **News Data**: Intraday news published $\ge 21:00$ UTC shifted to $T+1$ (`available_date`).
- **Fundamentals**: Quarterly statements available strictly on `public_release_date` ($T+45$ days).
- **Execution Timing**: Signals generated at Close $T$ execute at Open $T+1$.
