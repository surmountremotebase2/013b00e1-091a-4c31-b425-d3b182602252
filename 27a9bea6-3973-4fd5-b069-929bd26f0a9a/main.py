from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ATR
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):

    def __init__(self):
        # Define the ticker symbol for the asset you want to trade
        self.ticker = "CYBN"
        # Define the initial stop loss as None which will be set later
        self.initial_stop_loss = None

    @property
    def assets(self):
        # Return the list of assets that this strategy will use, in this case, just CYBN
        return [self.ticker]

    @property
    def interval(self):
        # Define the data interval to use for this strategy, daily intervals provide a broad overview of price movements
        return "1day"

    def run(self, data):
        # The 'data' parameter contains all the required data fetched by the Surmount trading framework

        # Calculate the ATR for CYBN with a lookback period of 14 days
        atr = ATR(self.ticker, data["ohlcv"], 14)
        
        # Position size to initially take - Here it's set to take full position (1) or none (0)
        allocation_size = 0
        
        # Ensure we have enough ATR data points to make decisions
        if len(atr) > 0:
            # Get the current ATR value, typically the last one in the generated list
            current_atr = atr[-1]
            
            # Get the latest close price for CYBN
            current_price = data["ohlcv"][-1][self.ticker]["close"]
            
            # Set an initial stop loss the first time when there's no initial stop loss set
            if self.initial_stop_loss is None:
                # The stop loss is set 2 ATR below the current price
                self.initial_stop_loss = current_price - (2 * current_atr)
            
            # If the current price is above the initial stop loss, we consider buying the stock
            # This is a simplified approach; you might want to add more conditions
            if current_price > self.initial_stop_loss:
                allocation_size = 1  # Buy
                # Update the stop loss every time the price moves favorably
                self.initial_stop_loss = max(self.initial_stop_loss, current_price - (2 * current_atr))
            else:
                allocation_size = 0  # Trigger stop loss, sell

            log(f"Current Price: {current_price}, Stop Loss: {self.initial_stop_loss}, ATR: {current_atr}")

        # Return the target allocation
        # allocation_size will be 1 (full investment in CYBN) or 0 (no investment in CYBN)
        return TargetAllocation({self.ticker: allocation_size})