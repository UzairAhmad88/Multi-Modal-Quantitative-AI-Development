"""
Real-Time Paper Trading Session Runner Script
Executes simulated live paper session feed processing and portfolio mark-to-market updates.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.realtime.scheduler.session_runner import PaperTradingSession
from src.data.market_loader import load_market_data


def main():
    print("[Real-Time Engine] Starting Paper Trading Session...")
    session = PaperTradingSession(initial_capital=100000.0)
    start_info = session.start_session()
    print(f"Session initialized: {start_info['session_id']}")

    symbols = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
    print(f"Streaming paper market feeds for symbols: {symbols}...")

    for sym in symbols:
        try:
            df = load_market_data(sym, start="2023-01-01")
            if df is not None and not df.empty:
                last_bar = df.tail(1).to_dict(orient="records")[0]
                last_bar["symbol"] = sym
                res = session.process_tick_or_bar(sym, last_bar)
                print(f"Processed bar [{sym}] Price: ${last_bar.get('close', 0.0):.2f} -> Signal: {res['signal']['direction']}")
        except Exception as e:
            print(f"Feed error for {sym}: {e}")

    stop_info = session.stop_session()
    print("\n" + "=" * 60)
    print("PAPER TRADING SESSION COMPLETED")
    print("=" * 60)
    print(f"Final Equity:   ${stop_info['final_equity']:,.2f}")
    print(f"Final Cash:     ${stop_info['final_cash']:,.2f}")
    print(f"Total Fills:    {stop_info['total_trades']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
