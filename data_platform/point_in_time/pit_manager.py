"""
Point-In-Time (PIT) Data Manager for Strict Temporal Availability and Leakage Prevention.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
import datetime


class PointInTimeManager:
    """Enforces strict Point-in-Time availability querying for news, fundamentals, and market data."""

    @staticmethod
    def get_available_news(news_df: pd.DataFrame, timestamp: str) -> pd.DataFrame:
        """Returns news articles available strictly at or before prediction timestamp."""
        if news_df.empty:
            return news_df
        df = news_df.copy()
        avail_col = "available_at" if "available_at" in df.columns else "published_at"
        ts = pd.to_datetime(timestamp, utc=True)
        df["_dt"] = pd.to_datetime(df[avail_col], utc=True)
        filtered = df[df["_dt"] <= ts].drop(columns=["_dt"])
        return filtered

    @staticmethod
    def get_available_fundamentals(fund_df: pd.DataFrame, timestamp: str) -> pd.DataFrame:
        """Returns fundamental statements available strictly at or before prediction timestamp."""
        if fund_df.empty:
            return fund_df
        df = fund_df.copy()
        avail_col = "available_at" if "available_at" in df.columns else "announcement_date"
        ts = pd.to_datetime(timestamp, utc=True)
        df["_dt"] = pd.to_datetime(df[avail_col], utc=True)
        filtered = df[df["_dt"] <= ts].drop(columns=["_dt"])
        return filtered

    @staticmethod
    def get_asof_market(market_df: pd.DataFrame, symbol: str, timestamp: str) -> Optional[pd.Series]:
        """Returns most recent available OHLCV bar as-of target timestamp."""
        if market_df.empty:
            return None
        df = market_df[market_df["symbol"].str.upper() == symbol.upper()].copy()
        if df.empty:
            return None
        ts = pd.to_datetime(timestamp, utc=True)
        df["_dt"] = pd.to_datetime(df["date"], utc=True)
        avail = df[df["_dt"] <= ts].sort_values(by="_dt")
        if avail.empty:
            return None
        return avail.iloc[-1].drop(labels=["_dt"])
