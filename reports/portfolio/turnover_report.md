# Portfolio Turnover & Transaction Drag Report

This report evaluates rebalance turnover and market impact drag calculated via `src/portfolio/costs.py`.

---

## 1. Market Impact Model
$$\text{Cost}_{\text{Total}} = \text{Commission} + \text{Slippage} + \gamma \times \sqrt{\frac{\text{Trade Value}}{\text{Daily Volume}}}$$

- Commission: `10.0 bps`
- Slippage: `5.0 bps`
- Impact coefficient $\gamma$: `0.10`
