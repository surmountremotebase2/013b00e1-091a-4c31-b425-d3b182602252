from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, BB, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker of interest.
        self.ticker = "CYBN"
    
    @property
    def assets(self):
        # List of assets this strategy will evaluate.
        return [self.ticker]

    @property
    def interval(self):
        # Data interval to be used for indicators calculation. 
        return "1day"

    def run(self, data):
        # Allocate 0 by default, indicate no position.
        allocation_dict = {self.ticker: 0}
        
        # Check if there's enough data for analysis.
        if len(data["ohlcv"]) > 20: # Assuming 20 as the minimum required for BB and somewhat for RSI.
            # Calculating technical indicators.
            rsi_val = RSI(self.ticker, data["ohlcv"], 14) # Calculating RSI with a 14-day window.
            bb_val = BB(self.ticker, data["ohlcv"], 20, 2) # Calculating Bollinger Bands with 20-day window and 2 std deviation. 

            # Defining conditions for buying based on technical analysis.
            # RSI below 30 suggests oversold conditions; price touching or dipping below BB lower band suggests potential buy point.
            is_buy_condition = (rsi_val[-1] < 30) and (data["ohlcv"][-1][self.ticker]["close"] <= bb_val["lower"][-1])
            
            # Log the calculated values for debugging and inspection.
            log(f"RSI: {rsi_val[-1]}, BB Lower: {bb_val['lower'][-1]}, Current Price: {data['ohlcv'][-1][self.ticker]['close']}")
            
            if is_buy_condition:
                # If buy conditions are met, allocate full portfolio towards the asset.
                allocation_dict[self.ticker] = 1
                log(f"Buy condition met for {self.ticker}. Allocating fully.")
            else:
                log(f"Conditions not met for buying {self.ticker}. No allocation.")
        else:
            log(f"Not enough data for analysis of {self.ticker}.")
        
        return TargetAllocation(allocation_dict)