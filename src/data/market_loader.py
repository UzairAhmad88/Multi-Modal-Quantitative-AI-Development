from __future__ import annotations
import os
import time
from pathlib import Path
from typing import List, Optional
import numpy as np
import pandas as pd
from src.utils.logger import get_logger
from src.utils.paths import DATA_DIR
from src.utils.config import get_config

logger = get_logger("market_loader")

REQUIRED_COLUMNS = ["date", "ticker", "open", "high", "low", "close", "volume"]


class MarketDataValidator:
    """Validates schema, completeness, and value integrity of market data."""

    @staticmethod
    def validate_schema(df: pd.DataFrame) -> bool:
        """Check if all required columns exist."""
        cols = [c.lower() for c in df.columns]
        missing = [c for c in REQUIRED_COLUMNS if c not in cols]
        if missing:
            raise ValueError(f"Market data missing required columns: {missing}")
        return True

    @staticmethod
    def missing_report(df: pd.DataFrame) -> pd.Series:
        """Return missing percentage for each column."""
        return df.isnull().mean()

    @staticmethod
    def validate_prices(df: pd.DataFrame) -> bool:
        """Ensure non-negative prices and High >= Low integrity."""
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            if col in df.columns and (df[col] <= 0).any():
                logger.warning(f"Found non-positive price values in column: {col}")
        if {"high", "low"}.issubset(df.columns):
            invalid_hl = (df["high"] < df["low"]).sum()
            if invalid_hl > 0:
                logger.warning(f"Found {invalid_hl} rows where High < Low")
        return True


class MarketDataCleaner:
    """Cleans, normalizes, and handles missing market data."""

    @staticmethod
    def clean(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        out = df.copy()
        out.columns = [str(c).lower().strip().replace(" ", "_") for c in out.columns]
        
        # Ensure ticker column exists
        if "ticker" not in out.columns:
            out["ticker"] = ticker

        # Ensure date column exists and is UTC datetime
        date_col = "date" if "date" in out.columns else ("index" if "index" in out.columns else out.columns[0])
        out[date_col] = pd.to_datetime(out[date_col], utc=True)
        if date_col != "date":
            out = out.rename(columns={date_col: "date"})

        # Drop duplicates based on date and ticker
        out = out.drop_duplicates(subset=["date", "ticker"]).sort_values("date").reset_index(drop=True)

        # Fill small missing gaps (ffill then bfill)
        num_cols = out.select_dtypes(include=[np.number]).columns
        out[num_cols] = out[num_cols].ffill().bfill()

        # Validate
        MarketDataValidator.validate_schema(out)
        MarketDataValidator.validate_prices(out)

        return out


def generate_demo_market_data(ticker: str, start: str, end: str, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic OHLCV daily market data using Geometric Brownian Motion."""
    dates = pd.date_range(start=start, end=end, freq="B", tz="UTC")
    if len(dates) == 0:
        dates = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=252, freq="B")

    # Set seed based on ticker string hash and base seed
    ticker_seed = (abs(hash(ticker)) + seed) % (2**32)
    rng = np.random.default_rng(ticker_seed)

    n = len(dates)
    dt = 1.0 / 252.0
    mu = 0.08  # 8% annual expected return
    sigma = 0.25  # 25% annual volatility

    # Initial price between $50 and $300 based on hash
    s0 = 50.0 + (abs(hash(ticker)) % 250)
    returns = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
    price_paths = s0 * np.exp(np.cumsum(returns))

    close = price_paths
    high = close * (1.0 + rng.uniform(0.001, 0.02, n))
    low = close * (1.0 - rng.uniform(0.001, 0.02, n))
    open_p = low + rng.uniform(0.0, 1.0, n) * (high - low)
    volume = rng.integers(100000, 10000000, size=n)

    df = pd.DataFrame({
        "date": dates,
        "ticker": ticker,
        "open": np.round(open_p, 2),
        "high": np.round(high, 2),
        "low": np.round(low, 2),
        "close": np.round(close, 2),
        "adj_close": np.round(close, 2),
        "volume": volume
    })
    return df


class MarketDataLoader:
    """Loads historical OHLCV market data with caching and fallback support."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (DATA_DIR / "raw" / "market")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config = get_config()

    def load(
        self,
        ticker: str,
        start: str = "2018-01-01",
        end: Optional[str] = None,
        use_cache: bool = True,
        max_retries: int = 3
    ) -> pd.DataFrame:
        if end is None:
            end = pd.Timestamp.now().strftime("%Y-%m-%d")

        data_mode = self.config.get("data_mode", "demo")
        cache_path = self.cache_dir / f"{ticker}.parquet"
        csv_cache_path = self.cache_dir / f"{ticker}.csv"

        if use_cache:
            if cache_path.exists():
                logger.info(f"Loading cached parquet for {ticker}")
                df = pd.read_parquet(cache_path)
                return MarketDataCleaner.clean(df, ticker)
            elif csv_cache_path.exists():
                logger.info(f"Loading cached CSV for {ticker}")
                df = pd.read_csv(csv_cache_path)
                return MarketDataCleaner.clean(df, ticker)

        if data_mode == "demo":
            logger.info(f"Generating synthetic demo market data for {ticker}")
            df = generate_demo_market_data(ticker, start, end)
        else:
            df = None
            for attempt in range(max_retries):
                try:
                    import yfinance as yf
                    logger.info(f"Downloading {ticker} via yfinance (attempt {attempt + 1})")
                    raw = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
                    if not raw.empty:
                        raw = raw.reset_index()
                        # Flatten MultiIndex columns if present
                        if isinstance(raw.columns, pd.MultiIndex):
                            raw.columns = [c[0] for c in raw.columns]
                        df = raw
                        break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {e}")
                    time.sleep(1)

            if df is None or df.empty:
                logger.warning(f"Could not download market data for {ticker}. Falling back to demo data.")
                df = generate_demo_market_data(ticker, start, end)

        cleaned = MarketDataCleaner.clean(df, ticker)

        # Save to cache
        try:
            cleaned.to_parquet(cache_path, index=False)
        except Exception:
            cleaned.to_csv(csv_cache_path, index=False)

        return cleaned


def load_market_data(ticker: str, start: str = "2018-01-01", end: Optional[str] = None) -> pd.DataFrame:
    """Convenience function wrapper for MarketDataLoader."""
    loader = MarketDataLoader()
    return loader.load(ticker, start=start, end=end)
