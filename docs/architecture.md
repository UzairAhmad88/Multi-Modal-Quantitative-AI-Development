# System Architecture

## Overview
The QUANT AI Platform is an end-to-end multi-modal quantitative finance research system combining Market OHLCV, Financial News NLP sentiment, and Fundamental Financial Statements.

```mermaid
graph TD
    A[Market Data] --> D[Temporal Feature Fusion]
    B[News & NLP] --> D
    C[Quarterly Fundamentals] --> D
    D --> E[Chronological Split]
    E --> F[Model Ensemble: XGBoost, LSTM, GRU, Transformer, MultiModalQuantNet]
    F --> G[Alpha Signal Generator]
    G --> H[Portfolio Allocator]
    H --> I[Risk Gate]
    I --> J[Event-Driven Backtester]
    J --> K[Research Reports]
```
