"""
Reconciliation Engine Module.
Treats connected Broker as Authoritative Source of Truth.
Compares Broker Account, Cash, Positions, Orders, and Fills against Local Database State.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from src.execution.broker.base import BrokerInterface, PositionInfo


@dataclass
class ReconciliationResult:
    is_reconciled: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    broker_cash: float = 0.0
    local_cash: float = 0.0
    cash_diff: float = 0.0
    broker_position_count: int = 0
    local_position_count: int = 0
    mismatches: List[Dict[str, Any]] = field(default_factory=list)
    status_summary: str = "RECONCILED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_reconciled": self.is_reconciled,
            "timestamp": self.timestamp,
            "broker_cash": self.broker_cash,
            "local_cash": self.local_cash,
            "cash_diff": self.cash_diff,
            "broker_position_count": self.broker_position_count,
            "local_position_count": self.local_position_count,
            "mismatches": self.mismatches,
            "status_summary": self.status_summary
        }


class ReconciliationEngine:
    """Automated Reconciliation Engine for broker vs local state audit."""

    def __init__(self, tolerance_cash: float = 0.01, tolerance_qty: float = 1e-4):
        self.tolerance_cash = tolerance_cash
        self.tolerance_qty = tolerance_qty

    def reconcile(
        self,
        broker: BrokerInterface,
        local_cash: float,
        local_positions: Dict[str, Dict[str, Any]]
    ) -> ReconciliationResult:
        """
        Execute full reconciliation pass:
        1. Cash Balance Audit
        2. Position Quantity Audit per Ticker
        3. Missing / Unknown Ticker Audit
        """
        if not broker.is_connected():
            return ReconciliationResult(
                is_reconciled=False,
                status_summary="RECONCILIATION_FAILED: Broker connection offline",
                mismatches=[{"type": "BROKER_OFFLINE", "details": "Broker is not connected"}]
            )

        account = broker.get_account()
        broker_cash = account.cash
        broker_positions = broker.get_positions()

        mismatches: List[Dict[str, Any]] = []

        # 1. Cash Audit
        cash_diff = abs(broker_cash - local_cash)
        if cash_diff > self.tolerance_cash:
            mismatches.append({
                "type": "CASH_MISMATCH",
                "symbol": "CASH",
                "broker_val": broker_cash,
                "local_val": local_cash,
                "diff": cash_diff,
                "details": f"Cash mismatch: Broker (${broker_cash:.2f}) vs Local (${local_cash:.2f})"
            })

        # 2. Position Audit
        all_symbols = set(broker_positions.keys()).union(set(local_positions.keys()))

        for sym in all_symbols:
            b_pos: Optional[PositionInfo] = broker_positions.get(sym)
            l_pos: Optional[Dict[str, Any]] = local_positions.get(sym)

            b_qty = b_pos.quantity if b_pos else 0.0
            l_qty = l_pos.get("quantity", 0.0) if l_pos else 0.0

            qty_diff = abs(b_qty - l_qty)
            if qty_diff > self.tolerance_qty:
                mismatches.append({
                    "type": "POSITION_MISMATCH",
                    "symbol": sym,
                    "broker_qty": b_qty,
                    "local_qty": l_qty,
                    "diff": qty_diff,
                    "details": f"Position mismatch for '{sym}': Broker ({b_qty}) vs Local ({l_qty})"
                })

        is_reconciled = (len(mismatches) == 0)
        summary = "RECONCILED_OK" if is_reconciled else f"MISMATCH_DETECTED ({len(mismatches)} discrepancies)"

        return ReconciliationResult(
            is_reconciled=is_reconciled,
            broker_cash=broker_cash,
            local_cash=local_cash,
            cash_diff=round(cash_diff, 2),
            broker_position_count=len(broker_positions),
            local_position_count=len(local_positions),
            mismatches=mismatches,
            status_summary=summary
        )
