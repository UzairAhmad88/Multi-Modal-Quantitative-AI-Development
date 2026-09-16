# QUANT AI Backtesting Methodology & Execution Protocol

## Execution Timing & Accounting Policy
- **Signal Generation**: Alpha signals and target portfolio weights are computed at market Close on trading day $T$.
- **Execution Timing**: Trades execute at market Open on trading day $T+1$ using the Open price with slippage and transaction fees.

---

## Transaction Cost & Friction Models
- **Transaction Commission**: 10.0 bps (0.10%) per trade.
- **Slippage Friction**: 5.0 bps (0.05%) execution penalty applied against trade direction.
- **Position Limits**: Maximum asset weight capped at 25.0% (`RiskEngine` gate).
- **Sector Exposure Limits**: Maximum sector weight capped at 40.0%.
- **Gross Leverage Cap**: Maximum gross exposure limited to 1.0x (No unconstrained leverage).
- **Drawdown Circuit Breaker**: If equity drawdown exceeds -20.0%, portfolio risk target is scaled down by 50%.
