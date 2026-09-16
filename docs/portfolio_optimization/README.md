# Phase 18: Portfolio Optimization, Position Sizing, Risk-Aware Allocation & Portfolio Construction

## 1. System Overview
The Portfolio Optimization Engine provides a mathematically rigorous bridge between multi-modal AI predictions and risk-managed investment portfolios.

It standardizes the complete portfolio construction pipeline:
```text
MULTI-MODAL MODEL -> ALPHA SIGNAL -> EXPECTED RETURN -> RISK ESTIMATOR -> PORTFOLIO OPTIMIZER -> CONSTRAINTS -> TRANSACTION COSTS -> REBALANCING ENGINE -> RISK ATTRIBUTION -> BACKTEST
```

---

## 2. Directory Architecture
```text
portfolio_optimization/
├── optimizers/           # Equal Weight, Inverse Vol, Risk Parity, Mean-Variance, Min-Var, Target Vol
├── constraints/          # ConstraintEngine (long-only, max/min weight, gross exposure, turnover limits)
├── objectives/           # ObjectiveEngine (return, variance, Sharpe, composite utility)
├── estimators/           # ExpectedReturnEstimator & CovarianceEstimator (Ledoit-Wolf shrinkage & PSD check)
├── position_sizing/      # PositionSizingEngine (Fractional Kelly, Volatility sizing, Risk budgeting)
├── transaction_costs/    # TransactionCostEngine (Commission, Spread, Slippage, Market Impact)
├── portfolio/            # RebalancingEngine (Threshold rebalancing, order share calculations)
├── risk/                 # RiskAttributionEngine (Marginal Contribution to Risk - MCR, % Risk Contribution)
├── attribution/          # PerformanceAttributionEngine (Realized asset return contribution)
├── scenarios/            # ScenarioEngine (Market shocks and volatility spike stress scenarios)
├── cli/                  # CLI tools (optimize.py, diagnostics.py, rebalance.py, compare.py)
└── manager.py            # Master PortfolioOptimizationManager orchestrating the system
```

---

## 3. CLI Tools
```bash
# Portfolio Optimization
python portfolio_optimization/cli/optimize.py --config configs/portfolio/multimodal.yaml

# Portfolio Diagnostics & Risk Attribution
python portfolio_optimization/cli/diagnostics.py --portfolio PORTFOLIO-001

# Rebalancing Trade Generation
python portfolio_optimization/cli/rebalance.py --portfolio PORTFOLIO-001

# Portfolio Comparison
python portfolio_optimization/cli/compare.py --portfolios PORTFOLIO-001 PORTFOLIO-002
```

---

## 4. REST API Endpoints
- `POST /api/v1/portfolio_opt/optimize`
- `GET  /api/v1/portfolio_opt/list`
- `GET  /api/v1/portfolio_opt/{id}`
- `POST /api/v1/portfolio_opt/rebalance`

---

## 5. Mathematical Integrity & Safety
- **No Direct Signal Scaling**: Signals are explicitly transformed via z-scores or percentile ranks before expected return estimation.
- **Ledoit-Wolf Shrinkage**: Covariance matrices are shrunk to handle high-dimensional noise and stabilized via Positive Semi-Definite (PSD) eigenvalue clipping.
- **Granular Cost Accounting**: Calculates commission, spread, and slippage prior to final order execution.
