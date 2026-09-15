# FastAPI REST Endpoints & Documentation

## Endpoints Summary
- `GET /health`: Health status & system readiness.
- `GET /market/{ticker}`: Historical OHLCV market data.
- `GET /news/{ticker}`: Financial news & sentiment scores.
- `GET /fundamentals/{ticker}`: Quarterly fundamental financial statements.
- `GET /features/{ticker}`: Feature store manifest & vectors.
- `POST /predict`: Baseline ML model return predictions.
- `POST /multimodal/predict`: `MultiModalQuantNet` deep fusion predictions.
- `GET /signals`: Active universe alpha signals.
- `GET /portfolio`: Risk-gated target portfolio allocations.
- `GET /risk`: Portfolio VaR, Sharpe, Beta, and drawdown metrics.
- `POST /backtest`: Trigger backtest simulations.
- `GET /models`: Model registry status.
- `GET /experiments`: MLflow experiment logs.
