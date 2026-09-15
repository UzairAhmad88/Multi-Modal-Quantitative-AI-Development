from __future__ import annotations
import pandas as pd
import numpy as np
from src.nlp.sentiment import score_sentiment_full

"""
NEWS TIME ALIGNMENT POLICY DOCUMENTATION:
------------------------------------------
News articles published AFTER market close (>= 21:00 UTC / 16:00 EST) cannot be known or acted upon
at the close of trading on day T. To eliminate future lookahead bias, any article published at or after
21:00 UTC is shifted to the NEXT trading day (T+1) as its 'available_date'.
Articles published before 21:00 UTC are available on day T.
"""


def align_news_timestamps(news_df: pd.DataFrame, market_close_hour_utc: int = 21) -> pd.DataFrame:
    """Align news publication timestamps to public market availability dates."""
    out = news_df.copy()
    out["published_at"] = pd.to_datetime(out["published_at"], utc=True)

    # Shift publication date to T+1 if published after market close
    is_after_close = out["published_at"].dt.hour >= market_close_hour_utc
    available_dt = out["published_at"].dt.floor("D")
    available_dt = np.where(is_after_close, available_dt + pd.Timedelta(days=1), available_dt)

    out["available_date"] = pd.to_datetime(available_dt, utc=True)
    return out


def aggregate_daily_sentiment(
    news_df: pd.DataFrame,
    timestamp_col: str = "published_at",
    ticker_col: str = "ticker"
) -> pd.DataFrame:
    """Process news articles and aggregate daily sentiment features per ticker."""
    if news_df.empty:
        return pd.DataFrame(columns=[
            "available_date", "ticker", "sentiment_mean", "sentiment_std", "sentiment_change",
            "positive_probability", "negative_probability", "neutral_probability",
            "news_count", "positive_news_count", "negative_news_count"
        ])

    aligned = align_news_timestamps(news_df)

    # Add sentiment scores and probabilities if not already computed
    if "sentiment_score" not in aligned.columns:
        scores, pos, neg, neu = score_sentiment_full(aligned["headline"].tolist())
        aligned["sentiment_score"] = scores
        aligned["positive_probability"] = pos
        aligned["negative_probability"] = neg
        aligned["neutral_probability"] = neu

    aligned["is_positive"] = (aligned["sentiment_score"] > 0.1).astype(int)
    aligned["is_negative"] = (aligned["sentiment_score"] < -0.1).astype(int)

    grouped = aligned.groupby(["available_date", ticker_col]).agg(
        sentiment_mean=("sentiment_score", "mean"),
        sentiment_std=("sentiment_score", "std"),
        positive_probability=("positive_probability", "mean"),
        negative_probability=("negative_probability", "mean"),
        neutral_probability=("neutral_probability", "mean"),
        news_count=("sentiment_score", "count"),
        positive_news_count=("is_positive", "sum"),
        negative_news_count=("is_negative", "sum")
    ).reset_index()

    grouped["sentiment_std"] = grouped["sentiment_std"].fillna(0.0)

    # Calculate daily sentiment change
    grouped = grouped.sort_values(["ticker", "available_date"]).reset_index(drop=True)
    grouped["sentiment_change"] = grouped.groupby("ticker")["sentiment_mean"].diff().fillna(0.0)

    return grouped


def add_rolling_sentiment_features(daily_sentiment: pd.DataFrame) -> pd.DataFrame:
    """Compute 1d, 3d, 5d, 7d rolling sentiment features per ticker."""
    if daily_sentiment.empty:
        return daily_sentiment

    out = daily_sentiment.sort_values(["ticker", "available_date"]).copy()

    for window in [1, 3, 5, 7]:
        out[f"sentiment_rolling_mean_{window}d"] = (
            out.groupby("ticker")["sentiment_mean"]
            .transform(lambda x: x.rolling(window, min_periods=1).mean())
        )
        out[f"news_count_rolling_{window}d"] = (
            out.groupby("ticker")["news_count"]
            .transform(lambda x: x.rolling(window, min_periods=1).sum())
        )

    return out
