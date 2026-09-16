# Market Data Providers & Normalization Protocol

This document details the provider abstractions and data normalization rules in `src/realtime/ingestion/provider.py`.

---

## 1. Supported Providers

1. **`MockMarketDataProvider`**: Deterministic synthetic quote and 15-minute bar generator for local offline testing.
2. **`YahooMarketDataProvider`**: Real-time and intraday bar fetching via `yfinance` with fallback to mock data if rate-limited.

---

## 2. Standard Normalized Schema

Every market quote/bar is normalized into the following schema:
```json
{
  "timestamp": "2026-09-16T13:45:00Z",
  "symbol": "AAPL",
  "open": 185.20,
  "high": 185.90,
  "low": 185.10,
  "close": 185.60,
  "volume": 25400
}
```
All timestamps are strictly timezone-aware UTC strings.
