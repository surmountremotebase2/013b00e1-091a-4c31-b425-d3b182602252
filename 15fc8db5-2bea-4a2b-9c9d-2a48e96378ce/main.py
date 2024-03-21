from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "CYBN"  # Replace with the correct ticker if different
        self.short_ema_length = 12
        self.long_ema_length = 26
        self.stop_loss_perc = 15  # 5% stop loss
        self.initial_investment_flag = True
        self.entry_price = 0
        
    @property
    def interval(self):
        return "1day"
    
    @property
    def assets(self):
        # Make sure only the targeted asset is returned
        return [self.ticker]

    @property
    def data(self):
        # No additional data fetching required for this strategy
        return []

    def run(self, data):
        # Retrieves the close prices for the targeted asset
        close_prices = [item[self.ticker]['close'] for item in data["ohlcv"]]
        
        # Calculate short and long EMAs
        short_ema = EMA(self.ticker, data["ohlcv"], self.short_ema_length)
        long_ema = EMA(self.ticker, data["ohlcv"], self.long_ema_length)
        
        allocation = 0
        if len(short_ema) > 0 and len(long_ema) > 0:
            # Make sure we have at least one EMA point to decide
            recent_short_ema = short_ema[-1]
            recent_long_ema = long_ema[-1]
            
            # Set initial investment flag and entry price on first transaction
            if self.initial_investment_flag:
                self.entry_price = close_prices[-1]
                self.initial_investment_flag = False
            
            # Implementing stop loss
            if close_prices[-1] < self.entry_price * self.stop_loss_perc:
                log("Stop loss triggered.")
                allocation = 0  # Exit position
            # Entry Logic: If short EMA crosses above long EMA
            elif recent_short_ema > recent_long_ema:
                log("Going long")
                allocation = 1  # Fully invested
            # Exit Logic: If short EMA crosses below long EMA
            elif recent_short_ema < recent_long_ema:
                log("Exiting position")
                allocation = 0  # Exit position
            
        return TargetAllocation({self.ticker: allocation})