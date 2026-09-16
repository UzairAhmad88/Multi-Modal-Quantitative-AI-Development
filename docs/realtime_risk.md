# Real-Time & Pre-Trade Risk Management

The `PreTradeRiskChecker` (`src/realtime/risk/pretrade_risk.py`) acts as an automated safety firewall protecting the platform during paper trading.

---

## 1. Pre-Trade Risk Rules & Thresholds

| Risk Rule | Threshold | Action on Violation |
|---|---|---|
| **Safety Lock** | `TRADING_ENABLED=False` | Reject Order (`REJECTED`) |
| **Single Position Limit** | `25.0%` of Portfolio Equity | Reject Order (`REJECTED`) |
| **Gross Exposure Limit** | `100.0%` of Portfolio Equity | Reject Order (`REJECTED`) |
| **Available Cash Check** | `Order Value <= Cash` | Reject Order (`REJECTED`) |
| **Max Daily Loss Limit** | `-5.0%` Portfolio Equity | Trigger `RISK_HALT` State |
| **Max Drawdown Limit** | `15.0%` Peak Equity | Trigger `RISK_HALT` State |
