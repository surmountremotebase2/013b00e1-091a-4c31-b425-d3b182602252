from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, Momentum
from surmount.data import *
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        self.asset = "CYBN"
        self.entry_date = None
        self.entry_price = 0
        self.min_holding_period = pd.Timedelta(days=365) # 1 year in days
        # Setting a stop loss at 20% below purchase price.
        self.stop_loss_percentage = 0.20
        self.trailing_stop_loss = 0
        self.has_bought = False
    
    @property
    def assets(self):
        return [self.asset]
    
    @property
    def interval(self):
        return "1day"
    
    @property
    def data(self):
        return [OHLCV(self.asset)]
    
    def run(self, data):
        ohlcv_data = data["ohlcv"]
        current_price = ohlcv_data[-1][self.asset]["close"]
        current_date = pd.to_datetime(ohlcv_data[-1][self.asset]["date"])
        allocation = {}
        
        if not self.has_bought:
            # Buy condition: Just for simplification, we're not checking momentum or SMA here.
            # You should normally analyze the historical data to predict growth
            self.has_bought = True
            self.entry_date = current_date
            self.entry_price = current_price
            self.trailing_stop_loss = current_price * (1 - self.stop_loss_percentage)
            allocation[self.asset] = 1 # 100% allocation
        else:
            # Update trailing stop loss if current price is higher than before
            if current_price > self.entry_price:
                gain = current_price - self.entry_price
                self.trailing_stop_loss = max(self.trailing_stop_loss, current_price - gain * 0.5)

            # Selling logic: after 1 year or if the stop loss is hit
            if ((current_date - self.entry_date) > self.min_holding_period and current_price > self.entry_price * 1.2) or \
               (current_price < self.trailing_stop_loss):
                allocation[self.asset] = 0 # Selling off
            else:
                allocation[self.asset] = 1 # Hold
            
        return TargetAllocation(allocation)