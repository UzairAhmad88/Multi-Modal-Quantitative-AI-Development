"""
Master Data Platform Manager unifying Ingestion, Data Quality, Point-in-Time Queries, Feature Store, and Dataset Construction.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from data_platform.ingestion.data_source import MarketDataSource, NewsDataSource, FundamentalDataSource
from data_platform.raw.raw_store import RawDataStore
from data_platform.normalization.normalizer import DataNormalizer
from data_platform.quality.quality_engine import DataQualityEngine
from data_platform.point_in_time.pit_manager import PointInTimeManager
from data_platform.features.feature_engine import FeatureEngine
from data_platform.feature_store.registry import FeatureStoreRegistry
from data_platform.cache.feature_cache import FeatureCache
from data_platform.datasets.dataset_builder import DatasetBuilder
from data_platform.versioning.snapshot_manager import SnapshotManager
from data_platform.lineage.lineage_tracer import DataLineageTracer
from data_platform.metadata.symbol_master import SymbolMaster, TradingCalendar


class DataPlatformManager:
    """Central Manager for Quantitative Data Platform & Feature Store."""

    def __init__(self):
        self.market_source = MarketDataSource()
        self.news_source = NewsDataSource()
        self.fund_source = FundamentalDataSource()

        self.raw_store = RawDataStore()
        self.normalizer = DataNormalizer()
        self.quality_engine = DataQualityEngine()
        self.pit_manager = PointInTimeManager()
        self.feature_engine = FeatureEngine()

        self.feature_registry = FeatureStoreRegistry()
        self.feature_cache = FeatureCache()
        self.dataset_builder = DatasetBuilder()
        self.snapshot_manager = SnapshotManager()
        self.lineage_tracer = DataLineageTracer()

        self.symbol_master = SymbolMaster()
        self.trading_calendar = TradingCalendar()

    def ingest_market_data(self, symbols: List[str], start_date: str = "2024-01-01", end_date: str = "2026-09-01") -> Dict[str, Any]:
        """Fetches, normalizes, validates, and stores market data."""
        raw_df = self.market_source.fetch(symbols, start_date, end_date)
        raw_path = self.raw_store.save_raw(raw_df, "market")
        norm_df = self.normalizer.normalize_market(raw_df)
        quality = self.quality_engine.validate_market(norm_df)

        return {
            "status": "SUCCESS",
            "source": "market",
            "rows": len(norm_df),
            "symbols": symbols,
            "raw_path": raw_path,
            "quality": quality
        }

    def ingest_news_data(self, symbols: List[str], start_date: str = "2024-01-01", end_date: str = "2026-09-01") -> Dict[str, Any]:
        """Fetches, normalizes, and stores news sentiment data."""
        raw_df = self.news_source.fetch(symbols, start_date, end_date)
        raw_path = self.raw_store.save_raw(raw_df, "news")
        norm_df = self.normalizer.normalize_news(raw_df)

        return {
            "status": "SUCCESS",
            "source": "news",
            "rows": len(norm_df),
            "symbols": symbols,
            "raw_path": raw_path
        }

    def ingest_fundamental_data(self, symbols: List[str], start_date: str = "2024-01-01", end_date: str = "2026-09-01") -> Dict[str, Any]:
        """Fetches, normalizes, and stores fundamental financial statement data."""
        raw_df = self.fund_source.fetch(symbols, start_date, end_date)
        raw_path = self.raw_store.save_raw(raw_df, "fundamentals")
        norm_df = self.normalizer.normalize_fundamentals(raw_df)

        return {
            "status": "SUCCESS",
            "source": "fundamentals",
            "rows": len(norm_df),
            "symbols": symbols,
            "raw_path": raw_path
        }

    def build_versioned_dataset(self, symbols: List[str], dataset_name: str = "multimodal_daily") -> Dict[str, Any]:
        """Orchestrates ingestion, feature engine, point-in-time alignment, and dataset creation."""
        mkt_df = self.normalizer.normalize_market(self.market_source.fetch(symbols, "2024-01-01", "2026-09-01"))
        news_df = self.normalizer.normalize_news(self.news_source.fetch(symbols, "2024-01-01", "2026-09-01"))
        fund_df = self.normalizer.normalize_fundamentals(self.fund_source.fetch(symbols, "2024-01-01", "2026-09-01"))

        res = self.dataset_builder.build_dataset(mkt_df, news_df, fund_df, config={"name": dataset_name})
        return res

    def get_point_in_time_data(self, symbol: str, timestamp: str) -> Dict[str, Any]:
        """Retrieves point-in-time available market, news, and fundamental data."""
        symbols = [symbol]
        mkt = self.market_source.fetch(symbols, "2024-01-01", timestamp[:10])
        asof_bar = self.pit_manager.get_asof_market(mkt, symbol, timestamp)

        news = self.news_source.fetch(symbols, "2024-01-01", timestamp[:10])
        avail_news = self.pit_manager.get_available_news(news, timestamp)

        fund = self.fund_source.fetch(symbols, "2024-01-01", timestamp[:10])
        avail_fund = self.pit_manager.get_available_fundamentals(fund, timestamp)

        return {
            "symbol": symbol,
            "query_timestamp": timestamp,
            "asof_market": asof_bar.to_dict() if asof_bar is not None else None,
            "available_news_count": len(avail_news),
            "available_fundamentals_count": len(avail_fund)
        }
