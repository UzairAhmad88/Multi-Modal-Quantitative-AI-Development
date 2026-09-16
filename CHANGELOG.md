# CHANGELOG

All notable changes to the **QUANT AI** platform are documented here.

## [1.0.0] - 2026-09-16

### Added
- Multi-modal data ingestion pipeline (Market OHLCV, Financial News NLP, Quarterly SEC Fundamentals).
- Temporal data synchronizer enforcing point-in-time $T+1$ news alignment and SEC filing release date merges.
- 247 standardized technical, NLP, fundamental, macro, and cross-asset quantitative features.
- Baseline ML models (XGBoost, Random Forest) and PyTorch Deep Learning models (LSTM, GRU, Temporal Transformer).
- CapStone `MultiModalQuantNet` neural architecture with learned softmax fusion attention.
- Alpha Engine with continuous alpha score normalization and discrete signal mapping (`BUY`, `STRONG BUY`, `NEUTRAL`).
- Risk Gate Portfolio Allocator enforcing position limit (25%), sector limit (40%), leverage (1.0x), and drawdown circuit breakers.
- Event-driven backtesting engine with 10 bps transaction fees and 5 bps slippage.
- Walk-forward time-series cross-validation and automated modality ablation study engine.
- FastAPI REST backend with 12 endpoints & Supabase Cloud integration with DDL migrations, Edge functions, and SQL seeds.
- Institutional Web OS research terminal (`frontend/`) and 12-page Streamlit research workspace (`dashboard/`).
- Full unit, integration, API, leakage, and UI test suite (65/65 tests passing).
- Docker and Docker-Compose containerization setup.
