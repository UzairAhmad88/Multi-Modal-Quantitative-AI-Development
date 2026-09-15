from __future__ import annotations
import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("data_synchronizer")

MARKET_OVERLAP_COLS = {"open", "high", "low", "close", "volume", "adj_close"}


def align_modalities(
    market_df: pd.DataFrame,
    daily_sentiment_df: pd.DataFrame | None = None,
    fundamentals_df: pd.DataFrame | None = None,
    on_col: str = "date"
) -> pd.DataFrame:
    """Synchronize Market, Daily Sentiment NLP, and Fundamental data using backward-looking merge_asof."""
    out = market_df.copy()
    out[on_col] = pd.to_datetime(out[on_col], utc=True)
    out = out.sort_values([on_col, "ticker"]).reset_index(drop=True)

    # 1. Align Daily News Sentiment (asof backward merge)
    if daily_sentiment_df is not None and not daily_sentiment_df.empty:
        news_df = daily_sentiment_df.copy()

        if "available_date" in news_df.columns:
            news_date_col = "available_date"
        elif "published_at" in news_df.columns:
            news_df["published_at"] = pd.to_datetime(news_df["published_at"], utc=True)
            news_df["available_date"] = news_df["published_at"].dt.floor("D")
            news_date_col = "available_date"
        elif on_col in news_df.columns:
            news_date_col = on_col
        else:
            raise KeyError(f"News dataset missing date column: available_date, published_at, or {on_col}")

        news_df[news_date_col] = pd.to_datetime(news_df[news_date_col], utc=True)

        # Drop overlapping market columns and redundant date keys
        cols_to_drop = [c for c in news_df.columns if c in MARKET_OVERLAP_COLS or (c == on_col and news_date_col != on_col)]
        if cols_to_drop:
            news_df = news_df.drop(columns=cols_to_drop)

        news_df = news_df.sort_values([news_date_col, "ticker"]).reset_index(drop=True)

        out = pd.merge_asof(
            out,
            news_df,
            left_on=on_col,
            right_on=news_date_col,
            by="ticker",
            direction="backward"
        )

        if news_date_col != on_col and news_date_col in out.columns:
            out = out.drop(columns=[news_date_col])

        sentiment_cols = [c for c in news_df.columns if c not in [news_date_col, "ticker", on_col]]
        for col in sentiment_cols:
            if col in out.columns:
                if "count" in col:
                    out[col] = out[col].fillna(0)
                else:
                    out[col] = out[col].ffill().fillna(0.0)

    # 2. Align Quarterly Fundamentals (asof backward merge based on public_release_date)
    if fundamentals_df is not None and not fundamentals_df.empty:
        fund_df = fundamentals_df.copy()
        if "public_release_date" in fund_df.columns:
            fund_date_col = "public_release_date"
        elif on_col in fund_df.columns:
            fund_date_col = on_col
        else:
            raise KeyError(f"Fundamentals missing date column: public_release_date or {on_col}")

        fund_df[fund_date_col] = pd.to_datetime(fund_df[fund_date_col], utc=True)

        # Drop overlapping market columns and redundant date keys
        cols_to_drop = [c for c in fund_df.columns if c in MARKET_OVERLAP_COLS or (c == on_col and fund_date_col != on_col)]
        if cols_to_drop:
            fund_df = fund_df.drop(columns=cols_to_drop)

        fund_df = fund_df.sort_values([fund_date_col, "ticker"]).reset_index(drop=True)

        out = pd.merge_asof(
            out,
            fund_df,
            left_on=on_col,
            right_on=fund_date_col,
            by="ticker",
            direction="backward"
        )

        if fund_date_col != on_col and fund_date_col in out.columns:
            out = out.drop(columns=[fund_date_col])

        fund_cols = [c for c in fund_df.columns if c not in [fund_date_col, "quarter_end_date", "ticker", on_col]]
        for col in fund_cols:
            if col in out.columns:
                out[col] = out[col].ffill().fillna(0.0)

    out = out.sort_values(["ticker", on_col]).reset_index(drop=True)
    return out
