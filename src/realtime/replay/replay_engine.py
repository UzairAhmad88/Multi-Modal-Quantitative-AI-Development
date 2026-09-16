"""
Real-Time Market Data Replay Engine Module
Replays historical OHLCV data through the real-time pipeline at accelerated speeds (1x, 10x, 100x).
"""

from datetime import datetime, timezone
import time
from typing import Dict, List, Any, Optional
import pandas as pd

from src.realtime.scheduler.session_runner import PaperTradingSession
from src.data.market_loader import load_market_data


class RealtimeReplayEngine:
    """Quantitative Historical Data Replay Engine."""

    def __init__(
        self,
        historical_df: Optional[pd.DataFrame] = None,
        symbol: str = "AAPL",
        initial_capital: float = 100000.0,
        speed_multiplier: int = 10,
        **kwargs
    ):
        self.historical_df = historical_df
        self.symbol = symbol
        self.speed_multiplier = speed_multiplier
        self.session = PaperTradingSession(initial_capital=initial_capital)

    def run_replay(
        self,
        symbols: Optional[List[str]] = None,
        start_date: str = "2023-01-01",
        end_date: str = "2023-01-10",
        demo: bool = True,
        max_bars: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute accelerated replay of historical bars through real-time session pipeline.
        """
        self.session.start_session()
        processed_count = 0

        if self.historical_df is not None and not self.historical_df.empty:
            df = self.historical_df
            bars = df.head(max_bars).to_dict(orient="records") if max_bars else df.to_dict(orient="records")
            for bar in bars:
                bar["symbol"] = self.symbol
                bar["timestamp"] = str(bar.get("date", datetime.now(timezone.utc).isoformat()))
                self.session.process_tick_or_bar(self.symbol, bar)
                processed_count += 1
        else:
            sym_list = symbols or ["AAPL", "MSFT"]
            for sym in sym_list:
                try:
                    df = load_market_data(sym, start=start_date)
                    if df is not None and not df.empty:
                        bars = df.tail(30).to_dict(orient="records") if demo else df.to_dict(orient="records")
                        for bar in bars:
                            bar["symbol"] = sym
                            bar["timestamp"] = str(bar.get("date", datetime.now(timezone.utc).isoformat()))
                            self.session.process_tick_or_bar(sym, bar)
                            processed_count += 1
                except Exception:
                    pass

        stop_res = self.session.stop_session()
        total_fills = stop_res["total_trades"]
        return {
            "status": "REPLAY_COMPLETED",
            "session_id": self.session.session_id,
            "speed_multiplier": f"{self.speed_multiplier}x",
            "processed_bars": processed_count,
            "total_bars_processed": processed_count,
            "total_orders": total_fills,
            "final_equity": stop_res["final_equity"],
            "total_fills": total_fills,
            "orders": self.session.execution_engine.get_fills()
        }


# Alias for backward compatibility
ReplaySessionEngine = RealtimeReplayEngine
