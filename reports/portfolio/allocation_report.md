# Asset Allocation & Constraint Compliance Report

All portfolio allocation results are validated through `src/portfolio/constraints.py`.

---

## 1. Constraint Rules

1. **Single Position Limit**: Max `25.0%` allocation per asset.
2. **Sector Limit**: Max `40.0%` aggregate weight per sector.
3. **Gross Exposure**: Max `100.0%` total portfolio leverage.
4. **Rebalance Threshold Filter**: Skip trade if $|\Delta w| < 2.0\%$.
