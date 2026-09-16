# Phase 19: Execution Engine & Market Microstructure OS

## Overview

Phase 19 adds a research-grade execution simulation layer between portfolio target weight allocations and realized portfolio positions. It transforms target portfolio allocations into realistic execution fills by modeling order management (OMS), market microstructure (slippage, latency, liquidity caps, market impact), execution algorithms (TWAP, VWAP, POV), accounting, analytics, CLI tools, REST APIs, and interactive Streamlit UI controls.

## Key Modules

### 1. Order Management & Validation (`execution/orders/`, `execution/order_management/`)
- `Order`: Standardized dataclass tracking `order_id`, `asset`, `side`, `quantity`, `order_type`, `status`, `filled_quantity`, `avg_fill_price`.
- `OrderValidator`: Verifies asset validity, positive quantity bounds, order limit prices, and portfolio size limits.
- `OrderManager`: Tracks active/filled/cancelled/rejected order queues and state audit trails.

### 2. Execution Algorithms (`execution/execution/algorithms/`)
- **MARKET**: Immediate single market order slice.
- **LIMIT**: Price-bound order matching at or better than target price.
- **TWAP**: Time-Weighted Average Price algorithm slicing parent order evenly across N time steps.
- **VWAP**: Volume-Weighted Average Price algorithm slicing parent order according to volume profile curve.
- **POV**: Percentage of Volume algorithm executing slices capped by market volume participation rate.

### 3. Market Microstructure Simulation (`execution/microstructure/`, `execution/slippage/`, `execution/latency/`, `execution/liquidity/`, `execution/market_impact/`)
- `OrderBook`: Bids, asks, depths, mid-price, and spread calculations.
- `SlippageEngine`: Directional execution price adjustment (BUY/COVER pays higher price, SELL/SHORT receives lower price) supporting fixed bps, volatility-based, and volume-based models.
- `LatencyEngine`: Models signal, decision, order submission, and execution delays.
- `LiquidityEngine`: Caps maximum fillable quantity per step using `max_participation_rate`.
- `MarketImpactEngine`: Square-root market impact penalty: $\text{Impact} = \gamma \cdot \sigma \cdot \sqrt{\text{Size} / \text{ADV}}$.

### 4. Portfolio Accounting (`execution/accounting/`)
- `PortfolioAccounting`: Updates cash balances, position quantities, average execution cost basis, realized PnL, unrealized PnL, and logs entries in `execution_ledger`.

### 5. Analytics & Attribution (`execution/analytics/`, `execution/attribution/`)
- `ImplementationShortfall`: Computes execution drag relative to decision price benchmark.
- `ExecutionSummaryReport`: Compiles fill rates, latency, shortfall, and cost metrics into neutral reports.
- `ExecutionAttributionEngine`: Attributes total cost into fees, spread, slippage, and market impact estimates.

## Usage

### CLI Tools
```bash
# Run execution simulation
python execution/cli/run_execution.py --portfolio PORTFOLIO-001 --config configs/execution/default.yaml

# Run backtest with execution simulation
python execution/cli/backtest_execution.py --strategy STRATEGY-001

# Inspect OMS state
python execution/cli/orders.py --status FILLED

# Generate execution report
python execution/cli/report.py --execution EXEC-001
```

### REST API
- `POST /execution/run`
- `GET /execution`
- `GET /execution/{id}`
- `GET /execution/{id}/orders`
- `GET /execution/{id}/fills`
- `GET /execution/{id}/costs`
- `GET /execution/{id}/analytics`
- `POST /execution/compare`

### Streamlit Workspace Page
- **Page 26**: `dashboard/pages/26_Execution_Simulation_OS.py`
