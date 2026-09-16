"""
Rebalance Engine Facade for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
import uuid
from datetime import datetime
from portfolio.core.rebalance import RebalanceEvent
from portfolio.rebalance.scheduler import RebalanceScheduler
from portfolio.rebalance.threshold import ThresholdRebalancer
from portfolio.costs.transaction import TransactionCostModel


class RebalanceEngine:
    """Central Rebalance Orchestrator managing execution triggers, turnover, and cost tracking."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.frequency = self.config.get("frequency", "weekly")
        self.threshold = self.config.get("threshold", 0.05)
        self.cost_model = TransactionCostModel(
            commission_bps=self.config.get("commission_bps", 5.0),
            bid_ask_spread_bps=self.config.get("bid_ask_spread_bps", 5.0),
        )

    def evaluate_rebalance_trigger(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        current_timestamp: str,
        last_rebalance_timestamp: Optional[str] = None,
        force_rebalance: bool = False,
    ) -> Tuple[bool, str]:
        if force_rebalance:
            return True, "FORCED"

        # Check calendar trigger
        calendar_trigger = RebalanceScheduler.should_rebalance_calendar(
            current_timestamp=current_timestamp,
            last_rebalance_timestamp=last_rebalance_timestamp,
            frequency=self.frequency,
        )
        if calendar_trigger:
            return True, "CALENDAR"

        # Check threshold trigger
        thresh_trigger, max_drift = ThresholdRebalancer.should_rebalance_threshold(
            current_weights=current_weights,
            target_weights=target_weights,
            threshold=self.threshold,
        )
        if thresh_trigger:
            return True, f"THRESHOLD_DRIFT ({max_drift:.4f})"

        return False, "NONE"

    def execute_rebalance(
        self,
        portfolio_id: str,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        timestamp: str,
        portfolio_value: float = 100000.0,
        executed_weights: Optional[Dict[str, float]] = None,
        reason: str = "SCHEDULED",
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> RebalanceEvent:
        """Process rebalancing event and preserve target vs executed portfolio states."""
        eff_executed = executed_weights if executed_weights is not None else target_weights.copy()

        # Calculate turnover sum(abs(executed - old))
        all_assets = set(current_weights.keys()).union(eff_executed.keys())
        turnover = sum(abs(eff_executed.get(a, 0.0) - current_weights.get(a, 0.0)) for a in all_assets)

        cost_res = self.cost_model.estimate_cost(
            target_weights=eff_executed,
            current_weights=current_weights,
            portfolio_value=portfolio_value,
            asset_metadata=asset_metadata,
        )

        event = RebalanceEvent(
            rebalance_id=f"REBAL-{uuid.uuid4().hex[:8].upper()}",
            portfolio_id=portfolio_id,
            timestamp=timestamp,
            old_weights=current_weights.copy(),
            target_weights=target_weights.copy(),
            executed_weights=eff_executed.copy(),
            turnover=float(turnover),
            estimated_cost=cost_res["total_cost"],
            rebalance_reason=reason,
            status="EXECUTED",
        )
        return event
