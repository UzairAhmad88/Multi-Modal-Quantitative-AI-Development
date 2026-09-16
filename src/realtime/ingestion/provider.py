"""
Market Data Provider Abstraction & Adapters
Normalizes live and mock market data into standard UTC tick/bar schemas.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd


class MarketDataProvider(ABC):
    """Abstract Base Class for Market Data Providers."""

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest quote for a symbol."""
        pass

    @abstractmethod
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch latest quotes for multiple symbols."""
        pass

    @abstractmethod
    def get_bars(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> pd.DataFrame:
        """Fetch historical bars dataframe."""
        pass

    @abstractmethod
    def get_latest_bar(self, symbol: str, timeframe: str = "15m") -> Dict[str, Any]:
        """Fetch the single latest bar."""
        pass


class MockMarketDataProvider(MarketDataProvider):
    """Simulated Market Data Provider for Offline Local Testing."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
        self.prices = {
            "AAPL": 185.50,
            "NVDA": 125.20,
            "MSFT": 420.10,
            "AMZN": 180.40,
            "GOOGL": 175.80,
        }

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        base_price = self.prices.get(sym, 100.0)
        price_change = np.random.normal(0, base_price * 0.002)
        curr_price = max(1.0, round(base_price + price_change, 2))
        self.prices[sym] = curr_price

        now_utc = datetime.now(timezone.utc).isoformat()
        return {
            "timestamp": now_utc,
            "symbol": sym,
            "bid": round(curr_price * 0.9995, 2),
            "ask": round(curr_price * 1.0005, 2),
            "last": curr_price,
            "volume": int(np.random.randint(100, 5000)),
        }

    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        return {sym.upper(): self.get_quote(sym) for sym in symbols}

    def get_bars(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> pd.DataFrame:
        sym = symbol.upper()
        base_price = self.prices.get(sym, 150.0)
        dates = pd.date_range(end=datetime.now(timezone.utc), periods=limit, freq="15min")

        returns = np.random.normal(0.0001, 0.003, limit)
        price_curve = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            "timestamp": [d.isoformat() for d in dates],
            "symbol": sym,
            "open": np.round(price_curve * (1 - 0.001), 2),
            "high": np.round(price_curve * (1 + 0.002), 2),
            "low": np.round(price_curve * (1 - 0.002), 2),
            "close": np.round(price_curve, 2),
            "volume": np.random.randint(1000, 50000, limit),
        })
        return df

    def get_latest_bar(self, symbol: str, timeframe: str = "15m") -> Dict[str, Any]:
        df = self.get_bars(symbol, timeframe, limit=1)
        return df.iloc[-1].to_dict()


class YahooMarketDataProvider(MarketDataProvider):
    """Live Market Data Adapter via yfinance."""

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            fast_info = ticker.fast_info
            last_price = float(fast_info.get("lastPrice", 150.0))
            now_utc = datetime.now(timezone.utc).isoformat()
            return {
                "timestamp": now_utc,
                "symbol": symbol.upper(),
                "bid": round(last_price * 0.9995, 2),
                "ask": round(last_price * 1.0005, 2),
                "last": round(last_price, 2),
                "volume": int(fast_info.get("lastVolume", 1000)),
            }
        except Exception:
            mock = MockMarketDataProvider()
            return mock.get_quote(symbol)

    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        return {sym.upper(): self.get_quote(sym) for sym in symbols}

    def get_bars(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> pd.DataFrame:
        try:
            import yfinance as yf
            interval_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "60m", "1d": "1d"}
            yf_interval = interval_map.get(timeframe, "15m")
            df = yf.download(symbol, period="5d", interval=yf_interval, progress=False)

            if df.empty:
                mock = MockMarketDataProvider()
                return mock.get_bars(symbol, timeframe, limit)

            df = df.reset_index()
            # Standardize columns
            col_rename = {}
            for col in df.columns:
                col_name = col[0] if isinstance(col, tuple) else str(col)
                c_lower = col_name.lower()
                if "date" in c_lower or "time" in c_lower:
                    col_rename[col] = "timestamp"
                elif "open" in c_lower:
                    col_rename[col] = "open"
                elif "high" in c_lower:
                    col_rename[col] = "high"
                elif "low" in c_lower:
                    col_rename[col] = "low"
                elif "close" in c_lower:
                    col_rename[col] = "close"
                elif "vol" in c_lower:
                    col_rename[col] = "volume"

            df = df.rename(columns=col_rename)
            df["symbol"] = symbol.upper()
            required = ["timestamp", "symbol", "open", "high", "low", "close", "volume"]
            df = df[[c for c in required if c in df.columns]]
            return df.tail(limit)
        except Exception:
            mock = MockMarketDataProvider()
            return mock.get_bars(symbol, timeframe, limit)

    def get_latest_bar(self, symbol: str, timeframe: str = "15m") -> Dict[str, Any]:
        df = self.get_bars(symbol, timeframe, limit=1)
        return df.iloc[-1].to_dict()
