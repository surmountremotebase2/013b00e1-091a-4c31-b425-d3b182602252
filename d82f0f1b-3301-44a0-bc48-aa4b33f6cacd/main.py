from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log
from datetime import datetime, timedelta

class TradingStrategy(Strategy):
    def __init__(self):
        # Only interested in CYBN for this strategy
        self.ticker = "CYBN"
        self.buy_price = None
        self.buy_date = None
        self.sell_date = None
        self.initial_investment = 0.0  # Placeholder, should be set based on portfolio size or capital allocation strategy
        self.stop_loss_percentage = 0.15  # 15% stop loss
        self.minimum_hold_period = timedelta(days=1)  # 1 year minimum hold period
    
    @property
    def assets(self):
        return [self.ticker]
    
    @property
    def interval(self):
        return "1day"  # Daily interval data for long term strategy
    
    def run(self, data):
        # Check if buying or selling conditions are met
        
        # Technical Indicators
        sma_short = SMA(self.ticker, data["ohlcv"], length=50)  # Short term SMA (50 days)
        sma_long = SMA(self.ticker, data["ohlcv"], length=200)  # Long term SMA (200 days)
        current_price = data["ohlcv"][-1][self.ticker]["close"]
        
        if self.buy_price is None:
            # Look for buying opportunity (Golden Cross)
            if sma_short[-1] > sma_long[-1] and sma_short[-2] < sma_long[-2]:
                # Condition met for buying
                self.buy_price = current_price
                self.buy_date = datetime.now()
                log(f"Buying {self.ticker} at {self.buy_price} on {self.buy_date}")
                return TargetAllocation({self.ticker: self.initial_investment})
        
        elif self.sell_date is None:
            # Implement Stop Loss
            if current_price < self.buy_price * (1 - self.stop_loss_percentage):
                log(f"Selling {self.ticker} at {current_price} due to stop loss.")
                return TargetAllocation({self.ticker: 0})
            
            # Check hold period and sell condition
            if datetime.now() - self.buy_date >= self.minimum_hold_period:
                # Assuming a simplistic profit-taking strategy after 1 year or more. Might need more sophisticated checks.
                log(f"Selling {self.ticker} at {current_price} after minimum hold period.")
                return TargetAllocation({self.ticker: 0})
        
        return TargetAllocation({self.ticker: 0})  # Default to no action