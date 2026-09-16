# Real-Time Architecture Specification

**System**: Multi-Modal Quantitative Intelligence Platform  
**Package**: `src/realtime/`  
**Version**: v2.6.0 Real-Time Release  

---

## 1. Overview

The Real-Time Engine provides intraday data streaming, 15-minute bar aggregation, live multi-modal feature calculation, alpha signal generation, pre-trade risk gating, paper order execution, trade ledger accounting, and pub/sub event broadcasting.

---

## 2. Component Pipeline Architecture

```text
HISTORICAL RESEARCH / LIVE STREAM
               │
               ▼
   MarketDataProvider (Mock / Yahoo)
               │
               ▼
   RealtimeBarBuilder (15m Intraday Bars)
               │
               ▼
   FeatureParityValidator
               │
               ▼
   RealtimeSignalEngine (Alpha Signals)
               │
               ▼
   PreTradeRiskChecker (Pre-Trade Gate)
               │
               ▼
   PaperExecutionEngine (Order State Machine)
               │
               ▼
   TradeLedger (Portfolio Accounting)
               │
               ▼
   RealtimeEventBus / WebSockets / Dashboard
```

---

## 3. Subsystem Descriptions

- **`ingestion/provider.py`**: Provider abstraction (`MarketDataProvider`) with `MockMarketDataProvider` and `YahooMarketDataProvider` adapters normalizing data into UTC timestamps.
- **`ingestion/session.py`**: `MarketSessionManager` evaluating exchange regular hours, pre-market, after-hours, weekends, and holidays.
- **`feature_engine/bar_builder.py`**: `RealtimeBarBuilder` aggregating 15-minute bars and `FeatureParityValidator` enforcing consistency between research and live features.
- **`signal_engine/engine.py`**: `RealtimeSignalEngine` evaluating model forecasts against long/short thresholds, cooldown timers, and position states.
- **`risk/pretrade_risk.py`**: `PreTradeRiskChecker` validating position size limits, capital availability, daily loss limits, drawdown halts, and the `TRADING_ENABLED=False` safety lock.
- **`execution/paper_engine.py`**: `PaperExecutionEngine` handling order creation, validation, submission, slippage simulation, transaction costs, and fill execution.
- **`storage/ledger.py`**: `TradeLedger` tracking cash, positions, realized P&L, unrealized P&L, and equity snapshots.
- **`monitoring/event_bus.py`**: Pub/Sub `RealtimeEventBus` broadcasting event payloads (`MARKET_UPDATE`, `SIGNAL_GENERATED`, `ORDER_FILLED`, `RISK_REJECTED`).
- **`replay/replay_engine.py`**: `ReplaySessionEngine` for deterministic historical bar replay testing.
