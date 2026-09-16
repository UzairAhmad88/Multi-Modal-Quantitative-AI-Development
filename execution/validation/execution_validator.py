"""
Execution Validation Engine: Checks execution simulation sanity, timestamp monotonicity, look-ahead bias, and price anomalies.
"""

from typing import List, Dict, Any, Tuple
from execution.orders.order import Order
from execution.fills.fill_engine import Fill


class ExecutionValidator:
    """Performs integrity checks on execution simulation outputs."""

    def validate_simulation(
        self,
        orders: List[Order],
        fills: List[Fill]
    ) -> Tuple[bool, List[str]]:
        """Verifies chronological order-to-fill integrity and non-zero prices."""
        issues = []

        for f in fills:
            if f.quantity <= 0:
                issues.append(f"Fill {f.fill_id} has non-positive quantity: {f.quantity}")
            if f.fill_price <= 0:
                issues.append(f"Fill {f.fill_id} has invalid non-positive price: {f.fill_price}")

        order_map = {o.order_id: o for o in orders}
        for f in fills:
            if f.order_id not in order_map:
                issues.append(f"Fill {f.fill_id} references unregistered order ID: {f.order_id}")
            else:
                o = order_map[f.order_id]
                if f.timestamp < o.timestamp:
                    issues.append(f"Look-ahead violation: Fill {f.fill_id} timestamp precedes order {o.order_id} creation")

        return len(issues) == 0, issues
