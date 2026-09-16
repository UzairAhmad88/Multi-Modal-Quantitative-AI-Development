# Technical Interview Preparation & Q&A

## Frequently Asked Questions

### Q1: Why use multi-modal feature fusion instead of pure price technicals?
**Answer**: Single-modality models suffer from regime fragility. Price momentum can reverse abruptly during news catalysts or earnings announcements. Fusing news NLP and fundamentals provides orthogonal signal sources that stabilize alpha predictions.

### Q2: How is lookahead data leakage explicitly prevented?
**Answer**: Through chronological train/val/test splits without shuffling, fitting scalers strictly on training data, shifting post-21:00 UTC news to $T+1$, merging SEC filings using `public_release_date`, and executing backtest fills at Open $T+1$ based on signals generated at Close $T$.

### Q3: Why can high model prediction accuracy produce poor backtest returns?
**Answer**: Model accuracy measures statistical fit (e.g. RMSE/MAE), ignoring transaction friction, slippage, position sizing, and risk limits. The backtesting engine enforces 10 bps fee and 5 bps slippage to measure real trading performance.
