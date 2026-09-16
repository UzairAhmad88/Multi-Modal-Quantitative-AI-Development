"""
Fee Engine for brokerage commissions, exchange fees, and cost integration with Phase 18.
"""

from typing import Dict, Any


class FeeEngine:
    """Calculates broker commissions and regulatory/exchange fees for simulated fills."""

    def __init__(
        self,
        commission_bps: float = 1.0,
        fixed_per_trade: float = 0.0,
        exchange_fee_bps: float = 0.1
    ):
        self.commission_bps = commission_bps
        self.fixed_per_trade = fixed_per_trade
        self.exchange_fee_bps = exchange_fee_bps

    def calculate_fees(self, trade_value: float) -> Dict[str, Any]:
        """Calculates total fee breakdown for a trade fill."""
        comm = (trade_value * (self.commission_bps / 10000.0)) + self.fixed_per_trade
        exch = trade_value * (self.exchange_fee_bps / 10000.0)
        total_fee = comm + exch

        return {
            "trade_value": round(trade_value, 2),
            "commission": round(comm, 2),
            "exchange_fee": round(exch, 2),
            "total_fee": round(total_fee, 2),
            "total_fee_bps": round((total_fee / trade_value * 10000.0), 2) if trade_value > 0 else 0.0
        }
