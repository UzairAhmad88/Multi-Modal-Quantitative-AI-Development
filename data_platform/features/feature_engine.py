import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.features.technical import add_technical_features


class FeatureEngine:
    """Computes technical, price, sentiment, and fundamental quantitative features."""

    def compute_features(self, market_df: pd.DataFrame, news_df: Optional[pd.DataFrame] = None, fund_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Computes unified feature dataframe from market, news, and fundamental sources."""
        if market_df.empty:
            return pd.DataFrame()

        df = market_df.copy()
        if "close" in df.columns:
            df["return"] = df.groupby("symbol")["close"].pct_change()
        df = add_technical_features(df)

        # Calculate RSI_14 explicitly if missing
        if "rsi" in df.columns:
            df["RSI_14"] = df["rsi"]
        elif "close" in df.columns:
            delta = df.groupby("symbol")["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss.replace(0, 1e-6))
            df["RSI_14"] = 100 - (100 / (1 + rs))

        # Add Volatility_20
        if "return" in df.columns:
            df["Volatility_20"] = df.groupby("symbol")["return"].transform(lambda x: x.rolling(20).std().fillna(0.01))
        else:
            df["Volatility_20"] = 0.01

        # Integrate News Sentiment if available
        if news_df is not None and not news_df.empty and "sentiment" in news_df.columns:
            sent_daily = news_df.groupby(["symbol", news_df["published_at"].str.slice(0, 10)])["sentiment"].mean().reset_index()
            sent_daily.columns = ["symbol", "date", "News_Sentiment_7D"]
            df = pd.merge(df, sent_daily, on=["symbol", "date"], how="left")
            df["News_Sentiment_7D"] = df.groupby("symbol")["News_Sentiment_7D"].ffill().fillna(0.0)
        else:
            df["News_Sentiment_7D"] = 0.0

        # Integrate Fundamentals if available
        if fund_df is not None and not fund_df.empty:
            if "eps" in fund_df.columns:
                fund_sub = fund_df[["symbol", "announcement_date", "eps"]].copy()
                fund_sub.columns = ["symbol", "date", "PE_Ratio"]
                df = pd.merge(df, fund_sub, on=["symbol", "date"], how="left")
                df["PE_Ratio"] = df.groupby("symbol")["PE_Ratio"].ffill().fillna(15.0)
            else:
                df["PE_Ratio"] = 15.0
            if "revenue" in fund_df.columns:
                rev_sub = fund_df[["symbol", "announcement_date", "revenue"]].copy()
                rev_sub.columns = ["symbol", "date", "Revenue_Growth"]
                df = pd.merge(df, rev_sub, on=["symbol", "date"], how="left")
                df["Revenue_Growth"] = df.groupby("symbol")["Revenue_Growth"].ffill().fillna(0.05)
            else:
                df["Revenue_Growth"] = 0.05
        else:
            df["PE_Ratio"] = 15.0
            df["Revenue_Growth"] = 0.05

        return df.fillna(0.0)
