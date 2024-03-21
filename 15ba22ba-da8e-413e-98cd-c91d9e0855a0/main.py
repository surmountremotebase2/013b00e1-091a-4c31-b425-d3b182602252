from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    @property
    def assets(self):
        # Target asset to trade
        return ["CYBN"]

    @property
    def interval(self):
        # Time interval for the trading data, adjusting for desired frequency
        return "1day"

    def run(self, data):
        # Initialize allocation to 0, indicating no investment by default
        cybn_stake = 0
        
        # Calculate the MACD and signal line to identify buy or sell signals
        macd_data = MACD("CYBN", data["ohlcv"]["CYBN"], fast=12, slow=26)
        if macd_data is not None:
            macd_line = macd_data["MACD"]
            signal_line = macd_data["signal"]
            
            # Check if there are enough data points to make a decision
            if len(macd_line) > 1 and len(signal_line) > 1:
                # If MACD crosses above signal line, it's a buy signal
                if macd_line[-1] > signal_line[-1] and macd_line[-2] < signal_line[-2]:
                    log("Buy signal for CYBN")
                    cybn_stake = 1  # Allocating 100% of the portfolio to CYBN
                
                # If MACD crosses below signal line, it's a sell/avoid signal
                elif macd_line[-1] < signal_line[-1] and macd_line[-2] > signal_line[-2]:
                    log("Sell signal for CYBN")
                    cybn_stake = 0  # Reducing the stake in CYBN to 0, considering it as a time to exit
        
        # Return the target allocation with the decided CYBN stake
        return TargetAllocation({"CYBN": cybn_stake})