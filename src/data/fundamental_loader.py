from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import numpy as np
import pandas as pd
from src.utils.logger import get_logger
from src.utils.paths import DATA_DIR
from src.utils.config import get_config

logger = get_logger("fundamental_loader")

REQUIRED_FUNDAMENTAL_COLUMNS = [
    "quarter_end_date", "public_release_date", "ticker", "revenue", "net_income",
    "eps", "ebitda", "free_cash_flow", "total_assets", "total_liabilities",
    "total_debt", "cash", "equity", "shares_outstanding"
]


class FundamentalValidator:
    """Validates fundamental schema and consistency."""

    @staticmethod
    def validate_schema(df: pd.DataFrame) -> bool:
        cols = set(df.columns)
        missing = [c for c in REQUIRED_FUNDAMENTAL_COLUMNS if c not in cols]
        if missing:
            raise ValueError(f"Fundamental data missing required columns: {missing}")
        return True


class FundamentalCleaner:
    """Cleans and standardizes quarterly fundamental financial statements."""

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["quarter_end_date"] = pd.to_datetime(out["quarter_end_date"], utc=True)
        out["public_release_date"] = pd.to_datetime(out["public_release_date"], utc=True)
        out["ticker"] = out["ticker"].astype(str).str.upper().str.strip()

        # Enforce public release date availability (release date must be after quarter end)
        invalid_dates = out["public_release_date"] < out["quarter_end_date"]
        if invalid_dates.any():
            logger.warning("Found release dates prior to quarter end; adjusting to quarter_end + 45 days")
            out.loc[invalid_dates, "public_release_date"] = out.loc[invalid_dates, "quarter_end_date"] + pd.Timedelta(days=45)

        out = out.drop_duplicates(subset=["public_release_date", "ticker"]).sort_values("public_release_date").reset_index(drop=True)
        FundamentalValidator.validate_schema(out)
        return out


def generate_demo_fundamentals(tickers: List[str], start_year: int = 2018, end_year: int = 2024, seed: int = 42) -> pd.DataFrame:
    """Generate quarterly fundamental statements with realistic financial metrics and public release dates."""
    rng = np.random.default_rng(seed)
    records = []

    for ticker in tickers:
        base_rev = 10000.0 + (abs(hash(ticker)) % 50000)
        base_shares = 1000.0
        equity = base_rev * 2.0
        debt = base_rev * 0.8

        for year in range(start_year, end_year + 1):
            for q, (m, d) in enumerate([(3, 31), (6, 30), (9, 30), (12, 31)], start=1):
                quarter_end = pd.Timestamp(year=year, month=m, day=d, tz="UTC")
                # SEC filing release typically 30-45 days after quarter end
                release_lag = int(rng.integers(30, 45))
                public_release = quarter_end + pd.Timedelta(days=release_lag)

                rev = base_rev * (1.0 + rng.uniform(0.01, 0.05))
                net_inc = rev * rng.uniform(0.10, 0.25)
                eps = net_inc / base_shares
                ebitda = net_inc * 1.5
                fcf = net_inc * rng.uniform(0.8, 1.2)
                assets = equity + debt
                liab = debt + (rev * 0.2)
                cash = rev * rng.uniform(0.15, 0.35)

                records.append({
                    "quarter_end_date": quarter_end,
                    "public_release_date": public_release,
                    "ticker": ticker,
                    "revenue": round(rev, 2),
                    "net_income": round(net_inc, 2),
                    "eps": round(eps, 2),
                    "ebitda": round(ebitda, 2),
                    "free_cash_flow": round(fcf, 2),
                    "total_assets": round(assets, 2),
                    "total_liabilities": round(liab, 2),
                    "total_debt": round(debt, 2),
                    "cash": round(cash, 2),
                    "equity": round(equity, 2),
                    "shares_outstanding": round(base_shares, 2)
                })

                base_rev = rev  # quarterly growth compounding

    df = pd.DataFrame(records)
    return FundamentalCleaner.clean(df)


class FundamentalLoader:
    """Loads quarterly fundamental data."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (DATA_DIR / "raw" / "fundamentals")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config = get_config()

    def load(self, tickers: Optional[List[str]] = None) -> pd.DataFrame:
        if tickers is None:
            tickers = self.config.get("data.universe", ["AAPL", "MSFT", "NVDA"])

        cache_path = self.cache_dir / "fundamentals.parquet"
        csv_path = self.cache_dir / "fundamentals.csv"

        if cache_path.exists():
            df = pd.read_parquet(cache_path)
            return FundamentalCleaner.clean(df)
        elif csv_path.exists():
            df = pd.read_csv(csv_path)
            return FundamentalCleaner.clean(df)

        df = generate_demo_fundamentals(tickers)
        try:
            df.to_parquet(cache_path, index=False)
        except Exception:
            df.to_csv(csv_path, index=False)

        return df


def load_fundamentals(ticker: Optional[str] = None, **kwargs) -> pd.DataFrame:
    loader = FundamentalLoader()
    df = loader.load(**kwargs)
    if ticker:
        return df[df["ticker"] == ticker].reset_index(drop=True)
    return df
