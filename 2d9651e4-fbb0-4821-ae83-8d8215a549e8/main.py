from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, EMA
from surmount.data import Asset
from datetime import datetime

class TradingStrategy(Strategy):
    def __init__(self):
        self.target_ticker = "CYBN"
        self.target_price = 4.50
        self.sell_below_price = 4.00  # defining a stop loss price
        self.buy_signal_strength = 0.5
        self.sell_signal_strength = -0.5
        self.holding_period = 365  # days
        self.last_buy_date = None

    @property
    def assets(self):
        return [self.target_ticker]

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        current_price = data["ohlcv"][-1][self.target_ticker]["close"]
        volume = data["ohlcv"][-1][self.target_ticker]["volume"]
        average_volume = SMA(self.target_ticker, data["ohlcv"], 10)[-1]
        signal_strength = (volume - average_volume) / average_volume

        allocation_dict = {}

        if self.last_buy_date:
            days_held = (datetime.now() - self.last_buy_date).days
        else:
            days_held = 0

        if current_price >= self.target_price:
            # Target price reached, sell all
            allocation_dict[self.target_ticker] = 0
            self.last_buy_date = None
        elif current_price <= self.sell_below_price or days_held >= self.holding_period:
            # Stop loss or holding period reached, sell all
            allocation_dict[self.target_ticker] = 0
            self.last_buy_date = None
        elif signal_strength >= self.buy_signal_strength and not self.last_buy_date:
            # Buy signal, strong volume, and not holding any stock
            allocation_dict[self.target_ticker] = 1
            self.last_buy_date = datetime.now()
        elif signal_strength <= self.sell_signal_strength and self.last_buy_date:
            # Weak volume and holding the stock, sell all
            allocation_dict[self.target_ticker] = 0
            self.last_buy_date = None
        else:
            # No action, keep current allocation
            return TargetAllocation({})  # Return an empty allocation to indicate no change

        return TargetAllocation(allocation_dict)