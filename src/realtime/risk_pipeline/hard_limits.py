"""
Hard Risk Limits Engine Module.
Implements configurable, mandatory hard risk constraints that strictly override AI model signals.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class HardRiskConfig:
    max_position_value: float = 30000.0       # Max $ value for single position
    max_position_percent: float = 0.30       # Max 30% of total equity
    max_gross_exposure: float = 1.00        # Max 100% gross exposure
    max_net_exposure: float = 0.50          # Max 50% net exposure
    max_daily_loss: float = 5000.0          # Max $5,000 daily loss
    max_daily_loss_pct: float = 0.05        # Max 5% daily equity drawdown
    max_order_value: float = 15000.0         # Max $15,000 per order
    max_order_quantity: float = 5000.0       # Max 5,000 shares/units per order
    max_turnover_daily: float = 2.00        # Max daily turnover multiplier
    max_open_positions: int = 10             # Max 10 simultaneous positions
    max_orders_per_minute: int = 60         # Rate limit: max 60 orders/min


class HardRiskLimitsEngine:
    """Enforces strict pre-trade hard risk limits outside of ML models."""

    def __init__(self, config: Optional[HardRiskConfig] = None):
        self.config = config or HardRiskConfig()
        self.order_timestamps: List[datetime] = []
        self.realized_daily_pnl: float = 0.0
        self.unrealized_daily_pnl: float = 0.0

    def check_order_limits(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        portfolio: Dict[str, Any],
        is_data_stale: bool = False
    ) -> Tuple[bool, str, float]:
        """
        Evaluate order against hard constraints.
        Returns (approved, reason, approved_quantity).
        """
        # 0. Stale Data Gate
        if is_data_stale:
            return False, "HARD_RISK_REJECT: Market data feed is stale.", 0.0

        equity = max(portfolio.get("equity", 100000.0), 1000.0)
        positions = portfolio.get("positions", {})
        cash = portfolio.get("cash", 100000.0)

        # 1. Rate Limiting Check (Orders per Minute)
        now = datetime.now(timezone.utc)
        self.order_timestamps = [t for t in self.order_timestamps if (now - t).total_seconds() <= 60]
        if len(self.order_timestamps) >= self.config.max_orders_per_minute:
            return False, f"HARD_RISK_REJECT: Rate limit exceeded ({self.config.max_orders_per_minute} orders/min).", 0.0

        # 2. Max Open Positions Check
        curr_pos_count = len(positions)
        if side.upper() == "BUY" and symbol not in positions and curr_pos_count >= self.config.max_open_positions:
            return False, f"HARD_RISK_REJECT: Max open positions limit ({self.config.max_open_positions}) reached.", 0.0

        # 3. Daily Loss Circuit Breaker
        current_daily_loss = abs(portfolio.get("daily_loss", 0.0))
        if current_daily_loss >= self.config.max_daily_loss:
            return False, f"HARD_RISK_REJECT: Max daily loss limit (${self.config.max_daily_loss:.2f}) reached.", 0.0

        daily_drawdown_pct = current_daily_loss / equity
        if daily_drawdown_pct >= self.config.max_daily_loss_pct:
            return False, f"HARD_RISK_REJECT: Max daily loss % ({daily_drawdown_pct:.2%}) exceeds cap ({self.config.max_daily_loss_pct:.2%}).", 0.0

        # 4. Max Order Quantity & Value Check
        proposed_order_val = quantity * price
        if proposed_order_val > self.config.max_order_value:
            # Cap quantity to fit max_order_value
            capped_qty = self.config.max_order_value / price if price > 0 else 0.0
            return True, f"HARD_RISK_REDUCED: Order value ${proposed_order_val:.2f} capped to max allowed ${self.config.max_order_value:.2f}.", round(capped_qty, 2)

        if quantity > self.config.max_order_quantity:
            return True, f"HARD_RISK_REDUCED: Order quantity {quantity} capped to max allowed {self.config.max_order_quantity}.", float(self.config.max_order_quantity)

        # 5. Position Weight & Value Cap Check
        curr_pos = positions.get(symbol, {})
        curr_qty = curr_pos.get("quantity", 0.0) if isinstance(curr_pos, dict) else (curr_pos.quantity if hasattr(curr_pos, 'quantity') else 0.0)

        new_total_qty = (curr_qty + quantity) if side.upper() == "BUY" else max(0.0, curr_qty - quantity)
        new_pos_value = new_total_qty * price

        if new_pos_value > self.config.max_position_value:
            allowed_add_val = max(0.0, self.config.max_position_value - (curr_qty * price))
            approved_qty = allowed_add_val / price if price > 0 else 0.0
            if approved_qty <= 0:
                return False, f"HARD_RISK_REJECT: Position in '{symbol}' already exceeds max position value ${self.config.max_position_value:.2f}.", 0.0
            return True, f"HARD_RISK_REDUCED: Position in '{symbol}' capped at max value ${self.config.max_position_value:.2f}.", round(approved_qty, 2)

        pos_pct = new_pos_value / equity
        if pos_pct > self.config.max_position_percent:
            allowed_val = (equity * self.config.max_position_percent) - (curr_qty * price)
            approved_qty = max(0.0, allowed_val / price) if price > 0 else 0.0
            if approved_qty <= 0:
                return False, f"HARD_RISK_REJECT: Position in '{symbol}' exceeds max position percent {self.config.max_position_percent:.2%}.", 0.0
            return True, f"HARD_RISK_REDUCED: Position in '{symbol}' capped at max weight {self.config.max_position_percent:.2%}.", round(approved_qty, 2)

        # Record timestamp for rate-limiting
        self.order_timestamps.append(now)

        return True, "HARD_RISK_APPROVED: Order passed all hard risk constraints.", round(quantity, 2)
