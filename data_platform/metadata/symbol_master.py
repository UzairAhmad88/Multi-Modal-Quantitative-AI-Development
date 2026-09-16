"""
Symbol Master and Trading Calendar Manager.
"""

from typing import Dict, Any, List, Optional
import pandas as pd


class SymbolMaster:
    """Manages ticker symbol reference database."""

    DEFAULT_SYMBOLS = {
        "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ", "asset_class": "equity", "currency": "USD", "status": "ACTIVE"},
        "MSFT": {"name": "Microsoft Corp.", "exchange": "NASDAQ", "asset_class": "equity", "currency": "USD", "status": "ACTIVE"},
        "NVDA": {"name": "NVIDIA Corp.", "exchange": "NASDAQ", "asset_class": "equity", "currency": "USD", "status": "ACTIVE"},
        "AMZN": {"name": "Amazon.com Inc.", "exchange": "NASDAQ", "asset_class": "equity", "currency": "USD", "status": "ACTIVE"},
        "GOOGL": {"name": "Alphabet Inc.", "exchange": "NASDAQ", "asset_class": "equity", "currency": "USD", "status": "ACTIVE"}
    }

    def __init__(self):
        self._symbols = self.DEFAULT_SYMBOLS.copy()

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        return self._symbols.get(symbol.upper())

    def list_symbols(self) -> List[Dict[str, Any]]:
        return [{"symbol": k, **v} for k, v in self._symbols.items()]


class TradingCalendar:
    """Handles market trading session calendar rules."""

    @staticmethod
    def is_trading_day(dt: pd.Timestamp) -> bool:
        """Returns False for weekend trading days."""
        return dt.weekday() < 5
