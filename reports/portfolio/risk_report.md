# Portfolio Risk Budgeting & Component Contribution Report

This document specifies the risk decomposition mathematics applied in `src/portfolio/risk_budgeting.py`.

---

## 1. Risk Contribution Equations

- **Portfolio Volatility**: $\sigma_p = \sqrt{w^T \Sigma w}$
- **Marginal Contribution to Risk (MCR)**: $\text{MCR}_i = \frac{(\Sigma w)_i}{\sigma_p}$
- **Component Risk Contribution (CRC)**: $\text{CRC}_i = w_i \times \text{MCR}_i$
- **Percentage Risk Contribution (PRC)**: $\text{PRC}_i = \frac{\text{CRC}_i}{\sigma_p}$

### Verification Property
$$\sum_{i=1}^{N} \text{CRC}_i = \sigma_p$$
Enforced within $10^{-5}$ numerical precision across all portfolio optimizers.
