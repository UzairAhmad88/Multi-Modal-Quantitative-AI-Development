"""
Execution Summary Report Generator: Compiles comprehensive neutral execution analytics.
"""

from typing import List, Dict, Any
from execution.orders.order import Order
from execution.fills.fill_engine import Fill
from execution.analytics.implementation_shortfall import ImplementationShortfall
from execution.analytics.slippage_analytics import SlippageAnalytics
from execution.analytics.liquidity_analytics import LiquidityAnalytics
from execution.analytics.fill_quality import FillQualityAnalytics
from execution.analytics.timing import TimingAnalytics


class ExecutionSummaryReport:
    """Generates consolidated execution quality report."""

    def __init__(self):
        self.shortfall_analyzer = ImplementationShortfall()
        self.slippage_analyzer = SlippageAnalytics()
        self.liquidity_analyzer = LiquidityAnalytics()
        self.quality_analyzer = FillQualityAnalytics()
        self.timing_analyzer = TimingAnalytics()

    def generate_report(
        self,
        orders: List[Order],
        fills: List[Fill],
        decision_prices: Dict[str, float],
        benchmarks: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Compiles neutral execution summary metrics."""
        shortfall = self.shortfall_analyzer.calculate_shortfall(fills, decision_prices)
        slippage = self.slippage_analyzer.analyze_slippage(fills)
        liquidity = self.liquidity_analyzer.analyze_liquidity(orders)
        quality = self.quality_analyzer.evaluate_quality(fills, benchmarks)
        timing = self.timing_analyzer.analyze_timing(fills)

        total_fees = sum(f.fees for f in fills)
        total_trade_volume = sum(f.quantity * f.fill_price for f in fills)

        return {
            "summary": {
                "total_orders": len(orders),
                "total_fills": len(fills),
                "total_trade_volume": round(total_trade_volume, 2),
                "total_fees": round(total_fees, 2),
                "fill_rate": liquidity["fill_rate"],
                "total_shortfall_dollars": shortfall["total_shortfall_dollars"],
                "total_shortfall_bps": shortfall["total_shortfall_bps"],
                "mean_latency_ms": timing["mean_latency_ms"]
            },
            "implementation_shortfall": shortfall,
            "slippage": slippage,
            "liquidity": liquidity,
            "fill_quality": quality,
            "timing": timing
        }
