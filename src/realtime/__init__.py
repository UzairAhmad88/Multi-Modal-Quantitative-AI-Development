"""
Multi-Modal Quant AI - Real-Time & Paper Trading Package
Provides real-time market data adapters, 15-minute bar builders, pre-trade risk checks,
paper execution engine, event bus, trade ledger, and historical replay sessions.
"""

from src.realtime.ingestion.provider import MarketDataProvider, MockMarketDataProvider, YahooMarketDataProvider
from src.realtime.ingestion.session import MarketSessionManager
from src.realtime.feature_engine.bar_builder import RealtimeBarBuilder, FeatureParityValidator
from src.realtime.signal_engine.engine import RealtimeSignalEngine
from src.realtime.risk.pretrade_risk import PreTradeRiskChecker
from src.realtime.execution.paper_engine import PaperExecutionEngine
from src.realtime.storage.ledger import TradeLedger
from src.realtime.monitoring.event_bus import RealtimeEventBus
from src.realtime.replay.replay_engine import ReplaySessionEngine

__all__ = [
    "MarketDataProvider",
    "MockMarketDataProvider",
    "YahooMarketDataProvider",
    "MarketSessionManager",
    "RealtimeBarBuilder",
    "FeatureParityValidator",
    "RealtimeSignalEngine",
    "PreTradeRiskChecker",
    "PaperExecutionEngine",
    "TradeLedger",
    "RealtimeEventBus",
    "ReplaySessionEngine",
]
