from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["CYBN"]
        self.entrance_ema_period = 50  # Period for the EMA to determine the trend
        self.pullback_ratio = 0.03  # Defines the pullback percentage from the last price to consider it a buying opportunity
        self.stop_loss_ratio = 0.10  # Percentage below the purchase price to set the stop loss

    @property
    def interval(self):
        return "1day"  # Using daily intervals
    
    @property
    def assets(self):
        return self.tickers
    
    def run(self, data):
        if "CYBN" not in data["ohlcv"]:  # Ensure data for CYBN is available
            log("CYBN data not available")
            return TargetAllocation({})
        
        data = data["ohlcv"]
        current_price = data[-1]["CYBN"]["close"]  # Get the latest closing price
        
        ema = EMA("CYBN", data, self.entrance_ema_period)  # Calculate the EMA for CYBN
        
        if len(ema) == 0 or current_price is None:
            log("EMA data not available")
            return TargetAllocation({})

        last_ema = ema[-1]
        pullback_entry_price = last_ema * (1 - self.pullback_ratio)

        allocation_ratio = 0
        
        # Check if the current price is above the EMA (uptrend) 
        # and has had a dip below the pullback entry price
        if current_price >= last_ema and current_price <= pullback_entry_price:
            allocation_ratio = 1  # Full allocation

        # Implement a dummy checking for tax efficiency and real-time stop-loss criteria
        # In a live strategy, this would involve checking for holding periods and dynamically adjusting allocations
        # and possibly interfacing with transaction history to ensure tax efficiency.

        return TargetAllocation({"CYBN": allocation_ratio})