from enum import Enum


class Side(Enum):
    BUY = 'Buy'
    SELL = 'Sell'


class PlaceOrderStatus(Enum):
    INSTRUMENT_NOT_FOUND = 100
    ACCOUNT_NOT_OPT_IN = 104
    MISSING_INVALID_PARAM = 101
    INSUFFICIENT_BALANCE = 105
    SUCCESS = 200
    MARKET_CLOSE = 99
