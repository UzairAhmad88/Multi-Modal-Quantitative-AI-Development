from __future__ import annotations
import uuid
from pathlib import Path
from typing import List, Optional
import numpy as np
import pandas as pd
from src.utils.logger import get_logger
from src.utils.paths import DATA_DIR
from src.utils.config import get_config

logger = get_logger("news_loader")

REQUIRED_NEWS_COLUMNS = [
    "article_id", "ticker", "published_at", "source", "headline", "article_text", "url"
]

DEMO_HEADLINES = {
    "bullish": [
        "{ticker} reports record quarterly revenue beating Wall Street estimates.",
        "Analyst upgrade raises target price for {ticker} following strong product demand.",
        "{ticker} announces strategic partnership to expand artificial intelligence offerings.",
        "{ticker} earnings call highlights robust margin expansion and positive forward guidance.",
        "Regulatory clearance approved for flagship {ticker} product line."
    ],
    "bearish": [
        "{ticker} misses Q3 earnings expectations as supply chain costs surge.",
        "Analyst downgrade cuts price target for {ticker} citing margin pressures.",
        "{ticker} faces regulatory scrutiny and potential antitrust investigation.",
        "Weak consumer demand triggers revenue guidance reduction for {ticker}.",
        "Executive departure at {ticker} raises strategic uncertainty among investors."
    ],
    "neutral": [
        "{ticker} schedules annual shareholder meeting for next month.",
        "{ticker} presents quarterly market update at industry conference.",
        "Trading volume for {ticker} remains steady amidst market consolidation.",
        "{ticker} completes routine debt refinancing transaction.",
        "Industry overview compares top technology giants including {ticker}."
    ]
}


class NewsValidator:
    """Validates schema and non-emptiness of news records."""

    @staticmethod
    def validate_schema(df: pd.DataFrame) -> bool:
        cols = set(df.columns)
        missing = [c for c in REQUIRED_NEWS_COLUMNS if c not in cols]
        if missing:
            raise ValueError(f"News dataset missing required columns: {missing}")
        return True


class NewsCleaner:
    """Cleans and standardizes raw news data."""

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "published_at" in out.columns:
            out["published_at"] = pd.to_datetime(out["published_at"], utc=True)

        out["headline"] = out["headline"].astype(str).str.strip()
        out["article_text"] = out["article_text"].astype(str).str.strip()
        out["ticker"] = out["ticker"].astype(str).str.upper().str.strip()

        # Deduplicate based on headline and published_at
        out = out.drop_duplicates(subset=["published_at", "ticker", "headline"]).sort_values("published_at").reset_index(drop=True)
        NewsValidator.validate_schema(out)
        return out


def generate_demo_news(tickers: List[str], start: str, end: str, count_per_ticker: int = 50, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic news articles with publication timestamps for specified tickers."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start=start, end=end, tz="UTC")

    records = []
    for ticker in tickers:
        ticker_dates = rng.choice(dates, size=min(count_per_ticker, len(dates)), replace=True)
        for dt in ticker_dates:
            # Add random intraday hour/minute offset
            pub_time = dt + pd.Timedelta(hours=int(rng.integers(6, 21)), minutes=int(rng.integers(0, 60)))
            category = rng.choice(["bullish", "bearish", "neutral"], p=[0.4, 0.35, 0.25])
            template = rng.choice(DEMO_HEADLINES[category])
            headline = template.format(ticker=ticker)
            text = f"Full article report regarding {ticker}. {headline} Analysts discuss market implications and key financial impacts."

            records.append({
                "article_id": str(uuid.uuid4())[:8],
                "ticker": ticker,
                "published_at": pub_time,
                "source": rng.choice(["Bloomberg", "Reuters", "Financial Times", "CNBC", "WSJ"]),
                "headline": headline,
                "article_text": text,
                "url": f"https://finance-news.demo/article/{ticker}/{pub_time.strftime('%Y%m%d')}"
            })

    df = pd.DataFrame(records)
    return NewsCleaner.clean(df)


class NewsLoader:
    """Loads and caches financial news articles."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (DATA_DIR / "raw" / "news")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config = get_config()

    def load(self, tickers: Optional[List[str]] = None, start: str = "2018-01-01", end: Optional[str] = None) -> pd.DataFrame:
        if tickers is None:
            tickers = self.config.get("data.universe", ["AAPL", "MSFT", "NVDA"])

        if end is None:
            end = pd.Timestamp.now().strftime("%Y-%m-%d")

        cache_path = self.cache_dir / "news_data.parquet"
        csv_cache_path = self.cache_dir / "news_data.csv"

        if cache_path.exists():
            logger.info("Loading cached news parquet")
            df = pd.read_parquet(cache_path)
            return NewsCleaner.clean(df)
        elif csv_cache_path.exists():
            logger.info("Loading cached news CSV")
            df = pd.read_csv(csv_cache_path)
            return NewsCleaner.clean(df)

        logger.info(f"Generating demo news pipeline data for universe: {tickers}")
        df = generate_demo_news(tickers, start, end)

        try:
            df.to_parquet(cache_path, index=False)
        except Exception:
            df.to_csv(csv_cache_path, index=False)

        return df


def load_news_data(source: str = "demo", **kwargs) -> pd.DataFrame:
    """Convenience wrapper for loading news data."""
    loader = NewsLoader()
    return loader.load(**kwargs)
