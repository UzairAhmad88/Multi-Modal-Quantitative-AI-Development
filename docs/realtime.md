# Real-Time Paper Trading & Execution Architecture Documentation

## Overview

The `src/realtime/` package provides a production-style, continuously running quantitative paper-trading platform.

```
LIVE DATA ➔ DATA VALIDATION ➔ ONLINE FEATURES ➔ SIGNAL ENGINE ➔ REBALANCER ➔ RISK GATE ➔ PAPER EXECUTION ➔ ACCOUNTING ➔ MONITORING
```

## Key Modules

- `src/realtime/ingestion/calendar.py`: `MarketCalendar` handling session hours and holidays.
- `src/realtime/ingestion/validation.py`: `DataValidator` checking staleness, gaps, duplicates.
- `src/realtime/feature_pipeline/online_features.py`: `OnlineFeatureEngine` maintaining rolling feature state.
- `src/realtime/signal_pipeline/realtime_signal.py`: `RealtimeSignalEngine` with debouncing and confidence checks.
- `src/realtime/portfolio_pipeline/rebalancer.py`: `PortfolioRebalancer` computing proposed trade sizes.
- `src/realtime/risk_pipeline/risk_gate.py`: `RealtimeRiskGate` enforcing pre-trade risk controls.
- `src/realtime/risk_pipeline/kill_switch.py`: `TradingKillSwitch` for safety circuit breaking.
- `src/realtime/execution/paper_execution.py`: `PaperExecutionEngine` simulating fills, slippage, and fees.
- `src/realtime/monitoring/health.py`: `SystemHealthMonitor` tracking health status and latency.
- `src/realtime/alerts/engine.py`: `AlertEngine` generating deduplicated alerts.
- `src/realtime/scheduler/session_runner.py`: `PaperTradingSession` orchestrating the complete real-time session.
- `src/realtime/replay/replay_engine.py`: `RealtimeReplayEngine` running accelerated historical replay simulations.

## CLI Commands

```bash
# Start paper trading session
python scripts/realtime.py start --config configs/realtime/paper.yaml

# Run accelerated historical market data replay
python scripts/realtime.py replay --config configs/realtime/replay.yaml

# Check system health
python scripts/realtime.py health

# Generate paper session report
python scripts/realtime.py report --session-id PAPER-SESSION-001
```
