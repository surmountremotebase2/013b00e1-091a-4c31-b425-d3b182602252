from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, BB, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker we are interested in
        self.ticker = "CYBN"

    @property
    def assets(self):
        # Indicate which asset this strategy is concerned with
        return [self.ticker]

    @property
    def interval(self):
        # Use daily interval for the strategy
        return "1day"
    
    def run(self, data):
        # Initial empty allocation, assuming we start with no position
        allocation = 0

        # Retrieve historical price data for the ticker
        ohlcv_data = data["ohlcv"]

        # Ensure we have enough data to compute indicators
        if len(ohlcv_data) >= 20:  # Arbitrary choice, adjust based on indicators' needs
            # Calculate the 14-period RSI
            rsi_values = RSI(self.ticker, ohlcv_data, 14)
            
            # Calculate the Bollinger Bands (20 periods by default, with a deviation of 2)
            bb_values = BB(self.ticker, ohlcv_data, 20, 2)

            # Calculate the 14-period ATR for volatility and stop loss calculation
            atr_values = ATR(self.ticker, ohlcv_data, 14)
            
            # Get the most recent values
            recent_rsi = rsi_values[-1]
            recent_close_price = ohlcv_data[-1][self.ticker]["close"]
            lower_band = bb_values["lower"][-1]
            atr_value = atr_values[-1]

            # Entry condition: RSI below 30 (oversold) and price touching or below the lower Bollinger Band
            if recent_rsi < 30 and recent_close_price <= lower_band:
                # Decide to take a position; here, we allocate a full 100% to CYBN.
                # This is a simplification. Adjust the allocation based on your risk appetite.
                allocation = 1

            # Here you would calculate your stop loss based on the ATR or other methods
            # This example does not execute trades or manage ongoing positions,
            # so the stop loss logic is not implemented in this script.
            # Normally, you might adjust your stop loss based on the recent ATR value, 
            # e.g., setting it 2*ATR below the entry price for long positions.

        # Log the decision for debugging purposes
        log(f"Allocating {allocation*100}% of portfolio to {self.ticker}")

        return TargetAllocation({self.ticker: allocation})