"""
Order & Fill Lineage Tracking Module.
Maintains complete institutional provenance from AI Signal through Risk Decision down to Broker Fills.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List


@dataclass
class OrderLineageRecord:
    internal_order_id: str
    signal_id: str
    model_id: str
    model_version: str
    environment: str
    symbol: str
    side: str
    quantity: float
    feature_snapshot_id: Optional[str] = None
    alpha_score: Optional[float] = None
    rebalancer_decision_id: Optional[str] = None
    risk_decision: str = "APPROVED"
    risk_reason: str = "Passed pre-trade risk checks"
    broker_order_id: Optional[str] = None
    broker_name: str = "PaperBroker"
    status: str = "CREATED"
    fill_id: Optional[str] = None
    fill_price: Optional[float] = None
    filled_quantity: float = 0.0
    commission: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LineageTracker:
    """In-memory and database lineage tracking engine for quantitative order lifecycle."""

    def __init__(self):
        self.records: Dict[str, OrderLineageRecord] = {}

    def register_lineage(self, record: OrderLineageRecord):
        self.records[record.internal_order_id] = record

    def update_broker_fill(self, internal_order_id: str, broker_order_id: str, fill_id: str, fill_price: float, filled_qty: float, status: str = "FILLED"):
        if internal_order_id in self.records:
            rec = self.records[internal_order_id]
            rec.broker_order_id = broker_order_id
            rec.fill_id = fill_id
            rec.fill_price = fill_price
            rec.filled_quantity = filled_qty
            rec.status = status

    def get_lineage(self, internal_order_id: str) -> Optional[Dict[str, Any]]:
        if internal_order_id in self.records:
            return self.records[internal_order_id].to_dict()
        return None

    def get_all_records(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.records.values()]
