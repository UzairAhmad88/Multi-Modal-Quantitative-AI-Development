# Paper Execution Engine Specifications

The `PaperExecutionEngine` (`src/realtime/execution/paper_engine.py`) simulates realistic order execution mechanics without financial risk.

---

## 1. Execution Cost & Slippage Model

- **Transaction Commission**: `10.0 bps` (0.10%) per trade value.
- **Execution Slippage**: `5.0 bps` (0.05%) default slippage added to BUY order fill prices and subtracted from SELL order fill prices.
- **Simulated Latency Delay**: `50ms` configurable execution delay simulating network transmission.

### Fill Price Calculation
$$\text{Fill Price}_{\text{BUY}} = \text{Market Price} \times \left(1 + \frac{\text{Slippage (bps)}}{10000}\right)$$
$$\text{Fill Price}_{\text{SELL}} = \text{Market Price} \times \left(1 - \frac{\text{Slippage (bps)}}{10000}\right)$$
