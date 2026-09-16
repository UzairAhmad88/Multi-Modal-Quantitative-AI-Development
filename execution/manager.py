"""
Execution Manager: Central Facade for End-to-End Execution Simulation, OMS, Accounting, and Analytics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from execution.trade_generator import TradeGenerator
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide
from execution.orders.order_status import OrderStatus
from execution.order_management.order_manager import OrderManager
from execution.execution.execution_engine import ExecutionEngine
from execution.execution.algorithms.market import MarketExecutionAlgorithm
from execution.execution.algorithms.limit import LimitExecutionAlgorithm
from execution.execution.algorithms.twap import TWAPExecutionAlgorithm
from execution.execution.algorithms.vwap import VWAPExecutionAlgorithm
from execution.execution.algorithms.pov import POVExecutionAlgorithm
from execution.accounting.portfolio_accounting import PortfolioAccounting
from execution.analytics.summary import ExecutionSummaryReport
from execution.attribution.execution_attribution import ExecutionAttributionEngine
from execution.validation.execution_validator import ExecutionValidator
from execution.scenarios.scenario_engine import ExecutionScenarioEngine


class ExecutionManager:
    """Master Orchestrator for Phase 19 Execution Simulation & Analytics OS."""

    def __init__(self, initial_cash: float = 100000.0, algorithm: str = "MARKET"):
        self.initial_cash = initial_cash
        self.algorithm_name = algorithm.upper()
        self.trade_generator = TradeGenerator()
        self.order_manager = OrderManager()
        self.execution_engine = ExecutionEngine(order_manager=self.order_manager)
        self.accounting = PortfolioAccounting(initial_cash=initial_cash)
        self.report_generator = ExecutionSummaryReport()
        self.attribution_engine = ExecutionAttributionEngine()
        self.validator = ExecutionValidator()
        self.scenario_engine = ExecutionScenarioEngine()
        self.execution_history: Dict[str, Dict[str, Any]] = {}

    def run_execution(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        market_snapshots: Dict[str, Dict[str, Any]],
        portfolio_id: str = "PORTFOLIO-001",
        algorithm: Optional[str] = None,
        scenario_name: str = "normal"
    ) -> Dict[str, Any]:
        """Runs full execution simulation pipeline from target weights to fills and accounting updates."""
        algo = algorithm.upper() if algorithm else self.algorithm_name
        exec_id = f"EXEC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        # 1. Extract reference prices
        prices = {a: s.get("close", s.get("price", 100.0)) for a, s in market_snapshots.items()}
        port_val = self.accounting.calculate_valuation(prices)["total_portfolio_value"]

        # 2. Generate required trades
        trades = self.trade_generator.generate_trades(
            current_weights=current_weights,
            target_weights=target_weights,
            prices=prices,
            portfolio_value=port_val
        )

        all_parent_orders: List[Order] = []
        all_child_orders: List[Order] = []
        all_fills: List[Any] = []
        decision_prices: Dict[str, float] = {}

        # Select algorithm strategy
        if algo == "TWAP":
            strategy = TWAPExecutionAlgorithm(num_intervals=5)
        elif algo == "VWAP":
            strategy = VWAPExecutionAlgorithm()
        elif algo == "POV":
            strategy = POVExecutionAlgorithm(target_participation_rate=0.05)
        else:
            strategy = MarketExecutionAlgorithm()

        for t in trades:
            asset = t["asset"]
            snap = market_snapshots.get(asset, {"close": t["price"]})
            snap_stressed = self.scenario_engine.get_stressed_snapshot(snap, scenario_name=scenario_name)
            decision_prices[asset] = snap_stressed.get("close", t["price"])

            # Create parent order
            parent_order = Order(
                asset=asset,
                side=t["side"],
                quantity=t["quantity"],
                order_type=OrderType.MARKET
            )
            self.order_manager.create_order(parent_order, price=t["price"])
            all_parent_orders.append(parent_order)

            # Generate slices
            slices = strategy.generate_slices(parent_order, market_volume=snap_stressed.get("volume", 100000.0))
            for child in slices:
                self.order_manager.create_order(child, price=t["price"])
                all_child_orders.append(child)

                # Execute slice
                fills = self.execution_engine.execute_order(child, snap_stressed)
                for f in fills:
                    all_fills.append(f)
                    self.accounting.process_fill(f, market_price=t["price"])

        # 3. Valuation & Analytics
        valuation = self.accounting.calculate_valuation(prices)
        benchmarks = {a: {"arrival_price": p, "vwap": p, "twap": p} for a, p in prices.items()}
        summary_report = self.report_generator.generate_report(all_child_orders, all_fills, decision_prices, benchmarks)
        cost_attribution = self.attribution_engine.attribute_execution_costs(all_fills)
        valid, issues = self.validator.validate_simulation(all_child_orders, all_fills)

        result = {
            "execution_id": exec_id,
            "portfolio_id": portfolio_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "algorithm": algo,
            "scenario": scenario_name,
            "total_trades_generated": len(trades),
            "parent_orders_count": len(all_parent_orders),
            "child_orders_count": len(all_child_orders),
            "fills_count": len(all_fills),
            "trades": trades,
            "orders": [o.to_dict() for o in all_child_orders],
            "fills": [f.to_dict() for f in all_fills],
            "valuation_after_execution": valuation,
            "summary_report": summary_report,
            "cost_attribution": cost_attribution,
            "validation": {"valid": valid, "issues": issues},
            "lineage": {
                "portfolio_id": portfolio_id,
                "execution_id": exec_id,
                "algorithm": algo,
                "scenario": scenario_name
            }
        }

        self.execution_history[exec_id] = result
        return result

    def get_execution_run(self, exec_id: str) -> Optional[Dict[str, Any]]:
        return self.execution_history.get(exec_id)
