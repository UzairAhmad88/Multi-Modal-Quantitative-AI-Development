# System Architecture Documentation

## System Flow Diagram

```
                         MULTI-MODAL QUANT AI
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
        MARKET DATA             NEWS             FUNDAMENTALS
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                        DATA QUALITY VALIDATOR
                                  │
                                  ▼
                        ONLINE FEATURE ENGINE
                                  │
                                  ▼
                         MULTIMODAL MODEL
                                  │
                                  ▼
                           SIGNAL ENGINE
                                  │
                                  ▼
                        PORTFOLIO REBALANCER
                                  │
                                  ▼
                         PRE-TRADE RISK GATE
                                  │
                       ┌──────────┴──────────┐
                       ▼                     ▼
                  APPROVED                REJECTED
                       │
                       ▼
                 PAPER EXECUTION ENGINE
                       │
                       ▼
                 PORTFOLIO & ACCOUNTING
                       │
              ┌────────┴────────┐
              ▼                 ▼
          MONITORING          ALERTS
              │                 │
              └────────┬────────┘
                       ▼
             MLOPS & RESEARCH REPORT
```

## Layer Descriptions

1. **Ingestion & Validation**: Loads market OHLCV bars, Finviz news, SEC fundamentals, and checks staleness ($<300\text{s}$), gaps, duplicates, and market session hours via `MarketCalendar`.
2. **Feature Pipeline**: Computes 240+ features across 7 feature groups. `OnlineFeatureEngine` maintains rolling state and verifies research-to-live feature parity.
3. **Multimodal Model Engine**: `MultiModalQuantNet` fuses market, sentiment, fundamental, and regime features using cross-attention and gating logic.
4. **Signal & Portfolio Engine**: `RealtimeSignalEngine` outputs predictions with confidence thresholds and debouncing. `PortfolioRebalancer` computes target asset weights.
5. **Pre-Trade Risk Gate & Safety**: `RealtimeRiskGate` audits position limits ($\le 25\%$), drawdown limits ($\le 10\%$), and stale data blocks. `TradingKillSwitch` safeguards system operation (`TRADING_MODE=paper`).
6. **Paper Execution Engine**: `PaperExecutionEngine` simulates fills with 5 bps slippage, 10 bps fees, and mark-to-market position accounting.
7. **MLOps & Lineage**: Persists dependency DAGs, dataset manifests, model artifacts, and metrics store. `ExperimentReproducer` enables deterministic out-of-sample re-runs.
