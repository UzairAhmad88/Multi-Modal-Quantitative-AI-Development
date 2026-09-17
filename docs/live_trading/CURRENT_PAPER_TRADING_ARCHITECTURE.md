# Current Paper Trading Architecture

**Multi-Modal Quant AI — System Audit & Baseline Architecture**  
**Document Status**: Baseline Audit Complete  
**Date**: September 2026  

---

## 1. Executive Summary

This document details the baseline Paper Trading architecture of the **Multi-Modal Quant AI System** prior to the implementation of controlled real-money trading functionality. The existing paper trading pipeline operates as an end-to-end simulated trading engine designed to evaluate live data ingestion, feature calculation, multi-modal AI inference, portfolio rebalancing, pre-trade risk gating, and simulated order execution.

---

## 2. Component Architecture Overview

The paper trading pipeline consists of 9 core sub-modules operating synchronously or semi-asynchronously:

```text
Incoming Market Tick / Bar
          │
          ▼
1. DATA VALIDATION (DataValidator / MarketCalendar)
          │
          ▼
2. ONLINE FEATURES (OnlineFeatureEngine)
          │
          ▼
3. MODEL INFERENCE & SIGNAL (RealtimeSignalEngine / Model Registry)
          │
          ▼
4. PORTFOLIO REBALANCING (PortfolioRebalancer)
          │
          ▼
5. PRE-TRADE RISK GATE (RealtimeRiskGate & TradingKillSwitch)
          │
          ▼
6. PAPER EXECUTION ENGINE (PaperExecutionEngine)
          │
          ▼
7. POSITION ACCOUNTING & MARK-TO-MARKET (PaperTradingSession)
          │
          ▼
8. MONITORING & ALERTING (SystemHealthMonitor / AlertEngine)
          │
          ▼
9. DATABASE & DASHBOARD PERSISTENCE (Supabase Client / API / Workstation UI)
```

---

## 3. Subsystem Breakdown

### 3.1 Data Source & Validation
- **Module**: `src.realtime.ingestion.validation.DataValidator` & `src.realtime.ingestion.calendar.MarketCalendar`
- **Function**: Receives incoming OHLCV bars or ticks, checks for missing attributes, volume anomalies, negative prices, and price change spikes (>15%). Validates data freshness against maximum latency thresholds.
- **Safety Action**: If market data is stale or invalid, an alert (`DATA_STALE_OR_INVALID`) is emitted and orders are blocked or the circuit breaker is tripped.

### 3.2 Online Feature Calculation
- **Module**: `src.realtime.feature_pipeline.online_features.OnlineFeatureEngine`
- **Function**: Maintains rolling market state buffers (SMA, RSI, Volatility) and calculates technical, news sentiment, and fundamental feature vectors dynamically per ticker.

### 3.3 Signal Generation & AI Inference
- **Module**: `src.realtime.signal_pipeline.realtime_signal.RealtimeSignalEngine`
- **Function**: Consumes online feature vectors and queries registered multi-modal AI models (Random Forest, XGBoost, LSTM, GRU, Transformer, Multi-Modal Fusion). Outputs forecast returns, directional signals (`BUY`, `SELL`, `HOLD`), and composite alpha scores.

### 3.4 Portfolio Rebalancing
- **Module**: `src.realtime.portfolio_pipeline.rebalancer.PortfolioRebalancer`
- **Function**: Translates composite signals and risk-adjusted forecasts into target portfolio weights and computes proposed trade delta (buy/sell quantity and value).

### 3.5 Pre-Trade Risk Gate & Kill Switch
- **Module**: `src.realtime.risk_pipeline.risk_gate.RealtimeRiskGate` & `src.realtime.risk_pipeline.kill_switch.TradingKillSwitch`
- **Function**:
  - `RealtimeRiskGate`: Enforces max position size limit (30%), max gross exposure (100%), max drawdown limit (10%), and data freshness checks. Modifies proposed order sizes (`APPROVED`, `REDUCED`, or `REJECTED`).
  - `TradingKillSwitch`: Global safety circuit breaker. Evaluates environment variable `TRADING_MODE` (default `paper`). Instantly halts session order execution if non-paper execution is detected without safety clearance.

### 3.6 Execution Simulation
- **Module**: `src.realtime.execution.paper_execution.PaperExecutionEngine`
- **Function**: Simulates order execution for market orders. Applies:
  - **Slippage**: 5.0 bps penalty added to buy price / subtracted from sell price.
  - **Commissions**: 10.0 bps transaction fee deducted from gross trade value.
  - Generates immutable paper order and fill records with simulated IDs (`ORD-*`, `FILL-*`).

### 3.7 Position Accounting & Mark-to-Market
- **Module**: `src.realtime.scheduler.session_runner.PaperTradingSession`
- **Function**: Maintains cash balance, position inventory, average cost basis, market value, unrealized P&L, and portfolio equity. Updates position values dynamically on every processed market bar.

### 3.8 Database & API Layer
- **Module**: `src.db.supabase_client` & `api.routes.realtime`
- **Function**: Persists generated signals to `ai_signals`, target allocations to `portfolio_allocations`, and risk state to `risk_metrics`. Exposes REST endpoints (`/api/realtime/*`, `/api/execution/*`) for monitoring.

### 3.9 UI & Workstation Visuals
- **Module**: `frontend/index.html` & Streamlit (`dashboard/pages/14_Realtime_Paper_Trading.py`)
- **Function**: Displays Top Bar status (`PAPER TRADING ONLY`, `REAL-MONEY DISABLED`), live signal feed, position table, and execution logs.

---

## 4. Key Limitations of Current Paper Trading Implementation

1. **Tight Coupling to Simulation**: The strategy and rebalancer directly instantiate `PaperExecutionEngine`, making it difficult to plug in real brokers without code modifications.
2. **Missing Real Broker Abstraction**: No unified `BrokerInterface` standardizing methods like `connect()`, `get_positions()`, `submit_order()`, `cancel_order()`, and `reconcile()`.
3. **Single Environment Flag**: System currently relies on informal `TRADING_MODE=paper` without strict multi-environment isolation (`BACKTEST`, `PAPER`, `SHADOW`, `SANDBOX`, `LIVE`).
4. **No Automated Reconciliation Engine**: Assumes local simulated positions match market reality without querying an authoritative external broker state.
5. **No Two-Key Live Authorization**: Does not enforce dual independent environment variables (`TRADING_ENV=LIVE` AND `LIVE_TRADING_ENABLED=true`) or confirmation tokens.
