from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, BB, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "CYBN"
        self.entry_rsi = 30 
        self.stop_loss_multiplier = 2 
        self.entry = False 
        self.stop_loss_price = 0 

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        # Using daily data for analysis
        return "1day"

    def run(self, data):
        current_price = data["ohlcv"][-1][self.ticker]["close"]
        rsi = RSI(self.ticker, data["ohlcv"], 14)[-1]
        bb = BB(self.ticker, data["ohlcv"], 20, 2)
        atr = ATR(self.ticker, data["ohlcv"], 14)[-1]

        allocation = 0

        if self.entry:
            # Entry conditions checking
            if rsi < self.entry_rsi and current_price <= bb["lower"][-1]:
                self.entry = True
                self.stop_loss_price = current_price - (self.stop_loss_multiplier * atr)
                allocation = 1
                log(f"Entering position for {self.ticker}. Stop loss set at {self.stop_loss_price}.")

        return TargetAllocation({self.ticker: allocation})