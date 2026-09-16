"""
Order Data Models and Enums.
"""

from enum import Enum


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    SHORT = "SHORT"
    COVER = "COVER"
    HOLD = "HOLD"


class TimeInForce(str, Enum):
    DAY = "DAY"
    GTC_SIMULATION = "GTC_SIMULATION"
    IOC = "IOC"
    FOK = "FOK"
