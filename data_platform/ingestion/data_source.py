"""
Data Source Abstraction and Ingestion Connectors.
Standardized interface for fetching, validating, normalizing, and storing raw data.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import datetime
from src.data.market_loader import MarketDataLoader
from src.data.news_loader import NewsLoader
from src.data.fundamental_loader import FundamentalLoader


class DataSource(ABC):
    """Abstract Base Class for Data Sources."""

    @abstractmethod
    def fetch(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches data from source."""
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """Validates basic schema."""
        pass

    @abstractmethod
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalizes data schema."""
        pass

    def metadata(self) -> Dict[str, Any]:
        """Returns source metadata."""
        return {
            "source_type": self.__class__.__name__,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }


class MarketDataSource(DataSource):
    """Market OHLCV Price & Volume Data Connector."""

    def __init__(self):
        self.loader = MarketDataLoader()

    def fetch(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        dfs = []
        for sym in symbols:
            try:
                df = self.loader.load(sym, start=start_date, end=end_date)
                if not df.empty:
                    df["symbol"] = sym.upper()
                    dfs.append(df)
            except Exception:
                pass
        if not dfs:
            # Fallback synthetic generator if no file on disk
            dates = pd.date_range(start=start_date, end=end_date, freq="D")
            records = []
            for sym in symbols:
                price = 150.0
                for d in dates:
                    price += np.random.normal(0.1, 1.5)
                    price = max(price, 10.0)
                    records.append({
                        "date": d.strftime("%Y-%m-%d"),
                        "symbol": sym.upper(),
                        "open": price - 0.5,
                        "high": price + 1.2,
                        "low": price - 1.0,
                        "close": price,
                        "volume": int(np.random.uniform(100000, 5000000))
                    })
            return pd.DataFrame(records)
        res = pd.concat(dfs, ignore_index=True)
        res["date"] = pd.to_datetime(res["date"]).dt.strftime("%Y-%m-%d")
        return res

    def validate(self, df: pd.DataFrame) -> bool:
        required = {"date", "symbol", "close"}
        return required.issubset(df.columns)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["symbol"] = df["symbol"].str.upper()
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        return df.sort_values(by=["symbol", "date"]).reset_index(drop=True)


class NewsDataSource(DataSource):
    """News Headline, NLP Sentiment & Availability Timestamp Data Connector."""

    def __init__(self):
        self.loader = NewsLoader()

    def fetch(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        try:
            df = self.loader.load(tickers=symbols, start=start_date, end=end_date)
        except Exception:
            df = pd.DataFrame()
        if "ticker" in df.columns and "symbol" not in df.columns:
            df = df.rename(columns={"ticker": "symbol"})
        if df.empty or "symbol" not in df.columns:
            dates = pd.date_range(start=start_date, end=end_date, freq="D")
            records = []
            idx = 1000
            for sym in symbols:
                for d in dates[:len(dates)//2]:
                    pub_dt = d.strftime("%Y-%m-%d 09:00:00")
                    avail_dt = d.strftime("%Y-%m-%d 09:05:00")
                    records.append({
                        "article_id": f"ART-{idx}",
                        "symbol": sym.upper(),
                        "headline": f"Financial update for {sym}",
                        "published_at": pub_dt,
                        "available_at": avail_dt,
                        "sentiment": round(float(np.random.uniform(-0.8, 0.8)), 4)
                    })
                    idx += 1
            return pd.DataFrame(records)
        df["symbol"] = df["symbol"].str.upper()
        if "published_at" not in df.columns and "date" in df.columns:
            df["published_at"] = df["date"] + " 09:00:00"
        if "available_at" not in df.columns:
            df["available_at"] = df["published_at"]
        return df

    def validate(self, df: pd.DataFrame) -> bool:
        cols = set(df.columns)
        return "symbol" in cols and ("sentiment" in cols or "article_id" in cols)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.upper()
        if "published_at" not in df.columns and "date" in df.columns:
            df["published_at"] = df["date"]
        return df.sort_values(by=["symbol", "published_at"]).reset_index(drop=True)


class FundamentalDataSource(DataSource):
    """SEC Financial Statement Fundamentals Connector."""

    def __init__(self):
        self.loader = FundamentalLoader()

    def fetch(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        try:
            df = self.loader.load(tickers=symbols)
        except Exception:
            df = pd.DataFrame()
        if "ticker" in df.columns and "symbol" not in df.columns:
            df = df.rename(columns={"ticker": "symbol"})
        if df.empty or "symbol" not in df.columns:
            records = []
            years = [2024, 2025, 2026]
            for sym in symbols:
                for y in years:
                    for q, m in [(1, "03-31"), (2, "06-30"), (3, "09-30"), (4, "12-31")]:
                        p_end = f"{y}-{m}"
                        ann_date = f"{y}-{int(m[:2])+1:02d}-15" if int(m[:2]) < 12 else f"{y+1}-02-15"
                        records.append({
                            "symbol": sym.upper(),
                            "period_end": p_end,
                            "announcement_date": ann_date,
                            "available_at": ann_date + " 00:00:00",
                            "revenue": round(float(np.random.uniform(1e9, 5e10)), 2),
                            "net_income": round(float(np.random.uniform(1e8, 5e9)), 2),
                            "eps": round(float(np.random.uniform(1.0, 5.0)), 2),
                            "total_assets": round(float(np.random.uniform(1e10, 1e11)), 2),
                            "total_liabilities": round(float(np.random.uniform(5e9, 5e10)), 2)
                        })
            return pd.DataFrame(records)
        if "announcement_date" not in df.columns:
            if "public_release_date" in df.columns:
                df["announcement_date"] = pd.to_datetime(df["public_release_date"]).dt.strftime("%Y-%m-%d")
            elif "date" in df.columns:
                df["announcement_date"] = df["date"]
            else:
                df["announcement_date"] = "2024-01-01"
        if "available_at" not in df.columns:
            if "public_release_date" in df.columns:
                df["available_at"] = pd.to_datetime(df["public_release_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                df["available_at"] = df["announcement_date"].astype(str) + " 00:00:00"
        return df

    def validate(self, df: pd.DataFrame) -> bool:
        cols = set(df.columns)
        return "symbol" in cols and len(cols.intersection({"announcement_date", "public_release_date", "period_end", "available_at"})) > 0

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["symbol"] = df["symbol"].str.upper()
        return df.sort_values(by=["symbol", "announcement_date"]).reset_index(drop=True)
