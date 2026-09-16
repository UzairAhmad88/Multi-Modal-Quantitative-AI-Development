"""
Command-Line Entry Point for Real-Time Paper Trading & Replay Sessions.
Usage:
  python scripts/run_realtime_paper.py --asset AAPL --duration 10 --replay
"""

import argparse
import sys
import os
import time

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.realtime.ingestion.provider import MockMarketDataProvider
from src.realtime.signal_engine.engine import RealtimeSignalEngine
from src.realtime.risk.pretrade_risk import PreTradeRiskChecker
from src.realtime.execution.paper_engine import PaperExecutionEngine
from src.realtime.storage.ledger import TradeLedger


def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Quant AI - Real-Time Paper Trading Runner")
    parser.add_argument("--asset", type=str, default="AAPL", help="Target asset ticker")
    parser.add_argument("--duration", type=int, default=10, help="Session duration in seconds")
    parser.add_argument("--replay", action="store_true", default=True, help="Run in historical replay mode")
    args = parser.parse_args()

    print("[PAPER TRADING] Starting Real-Time Paper Session...")
    print(f"   Asset: {args.asset}")
    print(f"   Duration: {args.duration}s")
    print(f"   Replay Mode: {args.replay}")
    print("   Safety Lock: TRADING_ENABLED=True (Simulated Paper Trading Only)")

    provider = MockMarketDataProvider()
    signal_engine = RealtimeSignalEngine()
    risk_checker = PreTradeRiskChecker(trading_enabled=True)
    execution_engine = PaperExecutionEngine()
    ledger = TradeLedger(100000.0)

    start_time = time.time()
    ticks_processed = 0

    while (time.time() - start_time) < args.duration:
        quote = provider.get_quote(args.asset)
        ticks_processed += 1
        price = quote["last"]

        # Signal generation
        pred_ret = (price % 5.0 - 2.5) / 100.0
        sig_res = signal_engine.process_features(
            symbol=args.asset,
            features={"close": price},
            predicted_return=pred_ret,
            confidence=0.80,
        )

        sig = sig_res["signal"]
        if sig in ["LONG", "SHORT"]:
            side = "BUY" if sig == "LONG" else "SELL"
            qty = 10.0
            snap = ledger.take_snapshot({args.asset: price})

            approved, reason = risk_checker.check_order(
                symbol=args.asset,
                side=side,
                quantity=qty,
                price=price,
                current_portfolio_value=snap["equity"],
                available_cash=snap["cash"],
                current_positions={args.asset: ledger.positions.get(args.asset, {}).get("quantity", 0.0)},
            )

            order = execution_engine.create_order(symbol=args.asset, side=side, quantity=qty)
            executed = execution_engine.execute_order(
                order_id=order["order_id"],
                market_price=price,
                is_approved=approved,
                rejection_reason=reason,
            )

            if executed["status"] == "FILLED":
                fill = execution_engine.fills[-1]
                ledger.record_fill(fill)

        ledger.take_snapshot({args.asset: price})
        time.sleep(0.5)

    final_snap = ledger.snapshots[-1] if ledger.snapshots else {}

    print("\n[OK] Paper Trading Session Complete!")
    print(f"   Total Ticks Processed: {ticks_processed}")
    print(f"   Total Orders Created: {len(execution_engine.orders)}")
    print(f"   Total Fills Executed: {len(execution_engine.fills)}")
    print(f"   Final Cash: ${final_snap.get('cash', 100000.0):,.2f}")
    print(f"   Final Portfolio Equity: ${final_snap.get('equity', 100000.0):,.2f}")
    print(f"   Total Realized P&L: ${final_snap.get('realized_pnl', 0.0):,.2f}")


if __name__ == "__main__":
    main()
