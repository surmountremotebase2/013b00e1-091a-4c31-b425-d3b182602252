from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker we are interested in
        self.ticker = "CYBN"
        # Historical peak price since the last buying point
        self.historical_peak = None
        # Stop loss percentage (20% drop from the peak)
        self.stop_loss_percent = 0.20

    @property
    def assets(self):
        # Define the asset we are trading
        return [self.ticker]

    @property
    def interval(self):
        # Use daily data for generating signals
        return "1day"

    def run(self, data):
        # Get close prices for calculating EMAs
        closes = [x[self.ticker]["close"] for x in data["ohlcv"]]
        
        # Calculate short-term (10-day) and long-term (30-day) EMAs
        short_ema = EMA(self.ticker, data["ohlcv"], 10)
        long_ema = EMA(self.ticker, data["ohlcv"], 30)
        
        if len(short_ema) == 0 or len(long_ema) == 0:
            # Not enough data to calculate EMAs, do not trade
            return TargetAllocation({})
        
        # Check if short-term EMA crosses above long-term EMA, indicating a buy signal
        if short_ema[-1] > long_ema[-1] and short_ema[-2] <= long_ema[-2]:
            self.historical_peak = closes[-1]  # Update the historical peak price
            return TargetAllocation({self.ticker: 1})  # Allocating 100% to CYBN
            
        # Update the historical peak if the current close price is higher
        if self.historical_peak is not None:
            if closes[-1] > self.historical_peak:
                self.historical_peak = closes[-1]
        
            # Check if the price has fallen more than 5% from the historical peak since the buy signal
            if (self.historical_peak - closes[-1]) / self.historical_peak > self.stop_loss_percent:
                # Sell signal based on the stop loss condition
                self.historical_peak = None  # Reset historical peak for the next cycle
                return TargetAllocation({self.ticker: 0})  # 0% allocation to CYBN
        
        # If neither buy nor sell conditions are met, maintain current holdings
        return TargetAllocation({})