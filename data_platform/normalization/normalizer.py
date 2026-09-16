"""
Data Normalization Engine for Standardizing Timestamps, Column Names, and Types.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class DataNormalizer:
    """Standardizes datasets across modalities to standard schemas and UTC timestamps."""

    @staticmethod
    def normalize_market(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df.columns = [c.lower() for c in df.columns]
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.upper()

        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.drop_duplicates(subset=["symbol", "date"]).sort_values(by=["symbol", "date"]).reset_index(drop=True)
        return df

    @staticmethod
    def normalize_news(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.upper()
        if "published_at" in df.columns:
            df["published_at"] = pd.to_datetime(df["published_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        if "available_at" in df.columns:
            df["available_at"] = pd.to_datetime(df["available_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        if "sentiment" in df.columns:
            df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce").fillna(0.0)
        return df.sort_values(by=["symbol", "published_at"]).reset_index(drop=True)

    @staticmethod
    def normalize_fundamentals(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.upper()
        if "announcement_date" in df.columns:
            df["announcement_date"] = pd.to_datetime(df["announcement_date"]).dt.strftime("%Y-%m-%d")
        if "available_at" in df.columns:
            df["available_at"] = pd.to_datetime(df["available_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        return df.sort_values(by=["symbol", "announcement_date"]).reset_index(drop=True)
