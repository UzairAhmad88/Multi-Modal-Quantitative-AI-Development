# System Architecture

```text
Market Data ────────> Market Features ──────┐
                                            │
News ───────────────> NLP Features ─────────┼─> Feature Fusion
                                            │
Fundamentals ───────> Fundamental Features ─┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                           XGBoost               LSTM              Transformer
                              └────────────────────┼────────────────────┘
                                                   ▼
                                             Alpha Engine
                                                   ▼
                                           Portfolio Engine
                                                   ▼
                                             Risk Engine
                                                   ▼
                                            Backtest Engine
                                                   ▼
                                           Evaluation Layer
                                                   ▼
                                           Quant Dashboard
```

## Design Rules

1. Provider-specific ingestion stays inside data adapters.
2. Feature engineering is independent from data providers.
3. Time alignment is backward-looking.
4. Models generate predictions; they do not place trades.
5. Alpha is separate from portfolio construction.
6. Risk controls cannot be bypassed by signals.
7. Backtests use only information available at each timestamp.
8. Dashboard code should consume prepared outputs instead of training large models in UI callbacks.
