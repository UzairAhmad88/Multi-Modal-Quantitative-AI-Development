"""
Broker Abstraction Layer for Multi-Modal Quant AI.
Provides unified interfaces and adapters for Paper, Shadow, Sandbox, and Real Brokers.
"""

from src.execution.broker.base import BrokerInterface, AccountInfo, OrderBook, PositionInfo
from src.execution.broker.paper import PaperBroker
from src.execution.broker.sandbox import SandboxBroker
from src.execution.broker.adapters.shadow import ShadowBroker

__all__ = [
    "BrokerInterface",
    "AccountInfo",
    "OrderBook",
    "PositionInfo",
    "PaperBroker",
    "SandboxBroker",
    "ShadowBroker",
]
