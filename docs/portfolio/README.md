# Phase 25: Portfolio Construction & Optimization Engine OS

## Overview

The **Portfolio Construction & Optimization Engine OS** (`portfolio/`) converts raw alpha signal predictions from the Multi-Modal Quant AI pipeline into production-grade risk-budgeted portfolio allocations. It enforces strict position, sector, asset-class, turnover, leverage, and liquidity constraints while penalizing non-linear market impact and transaction costs.

---

## Directory Structure

```text
portfolio/
├── __init__.py
├── core/               # Portfolio, Position, Weights, and Rebalance event models
├── optimization/       # Mean-Variance, Risk Parity, Min Variance, Equal Weight, Max Diversification, Constrained
├── sizing/             # Signal-based, Volatility targeting, Risk-budgeting, Confidence scaling
├── constraints/        # Position, Sector, Asset-class, Turnover, Leverage, Liquidity limits
├── costs/              # Transaction cost, Slippage, and Market Impact models
├── risk/               # Risk Attribution (MCR/PCR), Concentration (HHI, N_eff), Diversification ratio
├── rebalance/          # Calendar and Threshold rebalancing scheduler and engine
├── schemas/            # Pydantic schemas for requests and data validation
├── services/           # Unified PortfolioService business layer
├── api/                # REST API endpoints (/portfolio-v2/*)
├── cli/                # CLI tools (optimize, validate, risk, report)
├── configs/            # YAML configuration files for optimizers
├── reports/            # Markdown report generator
├── utils/              # Covariance estimators and Look-ahead protection filters
└── tests/              # Unit and integration test suite
```

---

## Core Capabilities

1. **Modular Optimizers**: Supports Mean-Variance ($\max w^T \mu - \frac{\lambda}{2} w^T \Sigma w$), Risk Parity (equal risk contribution), Minimum Variance, Maximum Diversification, Signal-Weighted, Equal-Weight, and Constrained quadratic programming solvers.
2. **Constraint Engine**: Evaluates position limits ($w_{\min} \le w_i \le w_{\max}$), sector exposure limits, turnover limits ($\sum |w_{\text{new}} - w_{\text{old}}| \le \text{max\_turnover}$), leverage limits, and ADV participation liquidity limits.
3. **Transaction Cost Penalties**: Cost-aware optimization incorporates explicit commission, bid-ask spread, and non-linear square-root market impact penalties ($w^T \Sigma w + \gamma \cdot \text{cost}$).
4. **Risk Attribution & Concentration**: Computes Marginal Contribution to Risk (MCR), Percentage Contribution to Risk (PCR), Herfindahl-Hirschman Index (HHI), and Effective Number of Assets ($N_{\text{eff}} = 1 / \sum w_i^2$).
5. **Rebalancing Engine**: Automated calendar (daily, weekly, monthly, quarterly) and threshold-based drift rebalancing.

---

## Usage Examples

### Python API

```python
from portfolio.services.portfolio_service import PortfolioService

service = PortfolioService()
port = service.create_portfolio(name="Multi-Asset Quant Strategy", assets=["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"])

# Optimize portfolio using Mean-Variance with risk aversion lambda=1.5
opt_result = service.optimize_portfolio(
    portfolio_id=port.portfolio_id,
    method="mean_variance",
    alpha_scores={"AAPL": 0.05, "MSFT": 0.04, "GOOGL": 0.02, "AMZN": 0.06, "NVDA": 0.09},
    constraints_override={"risk_aversion": 1.5, "max_position_weight": 0.30},
)

print(opt_result["target_weights"])
```

### CLI Tool

```bash
python portfolio/cli/optimize.py --portfolio-id PORT-001 --method risk_parity --report
```

---

## REST API Endpoints

- `POST /portfolio-v2/create`: Initialize new portfolio.
- `GET /portfolio-v2/{id}`: Retrieve portfolio state.
- `POST /portfolio-v2/optimize`: Run portfolio optimization.
- `POST /portfolio-v2/validate`: Validate constraint compliance.
- `GET /portfolio-v2/{id}/risk`: Get risk attribution (MCR, PCR, HHI).
- `POST /portfolio-v2/{id}/rebalance`: Execute rebalance event.
- `GET /portfolio-v2/{id}/report`: Generate human-readable Markdown report.
