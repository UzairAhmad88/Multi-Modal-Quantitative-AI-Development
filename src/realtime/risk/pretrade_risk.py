"""
Pre-Trade Risk Engine Module
Validates real-time signals and paper orders against capital, exposure, daily loss limits,
drawdown halts, and the mandatory TRADING_ENABLED safety lock.
"""

from typing import Dict, List, Any, Tuple


class PreTradeRiskChecker:
    """Pre-Trade Risk Control & Order Validation Engine."""

    def __init__(
        self,
        trading_enabled: bool = False,
        max_position_pct: float = 0.25,
        max_gross_exposure: float = 1.0,
        max_daily_loss_pct: float = 0.05,
        max_drawdown_limit: float = 0.15,
    ):
        self.trading_enabled = trading_enabled
        self.max_position_pct = max_position_pct
        self.max_gross_exposure = max_gross_exposure
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_limit = max_drawdown_limit

        self.daily_pnl_pct: float = 0.0
        self.current_drawdown_pct: float = 0.0
        self.is_halted: bool = False

    def check_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        current_portfolio_value: float,
        available_cash: float,
        current_positions: Dict[str, float],
    ) -> Tuple[bool, str]:
        """
        Validate proposed paper order against pre-trade risk controls.
        """
        # 1. Safety Lock Check
        if not self.trading_enabled:
            return False, "REJECTED: TRADING_ENABLED safety lock is set to False"

        # 2. Risk Halt Check
        if self.is_halted:
            return False, "REJECTED: System is in RISK_HALT state due to prior breach"

        # 3. Daily Loss Limit Check
        if self.daily_pnl_pct <= -self.max_daily_loss_pct:
            self.is_halted = True
            return False, f"REJECTED: Daily loss limit breached ({self.daily_pnl_pct*100:.2f}%)"

        # 4. Max Drawdown Check
        if self.current_drawdown_pct >= self.max_drawdown_limit:
            self.is_halted = True
            return False, f"REJECTED: Max drawdown limit breached ({self.current_drawdown_pct*100:.2f}%)"

        # 5. Capital & Order Value Check
        order_value = quantity * price
        if side.upper() == "BUY" and order_value > available_cash:
            return False, f"REJECTED: Insufficient cash (Required: ${order_value:,.2f}, Available: ${available_cash:,.2f})"

        # 6. Single Position Limit Check
        curr_pos_val = current_positions.get(symbol.upper(), 0.0) * price
        new_pos_val = curr_pos_val + order_value if side.upper() == "BUY" else curr_pos_val - order_value
        new_pos_pct = abs(new_pos_val) / (current_portfolio_value + 1e-8)

        if new_pos_pct > self.max_position_pct:
            return False, f"REJECTED: Single position limit exceeded ({new_pos_pct*100:.2f}% > {self.max_position_pct*100:.2f}%)"

        return True, "APPROVED: Pre-trade risk checks passed"
