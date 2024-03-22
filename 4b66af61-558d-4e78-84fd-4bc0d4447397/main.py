from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
import numpy as np
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        # Add your tickers here
        self.tickers = ["CYBN", "MNMD"]
    
    @property
    def interval(self):
        # Define the interval of your data (e.g., daily, hourly)
        return "1day"
    
    @property
    def assets(self):
        # Return the list of assets this strategy is concerned with
        return self.tickers
    
    @property
    def data(self):
        # If you need to fetch specific data for your strategy, define it here
        return []
    
    def run(self, data):
        # The main logic of the trading strategy
        try:
            # Extract volumes from the OHLCV data
            cybn_volumes = np.array([i["CYBN"]["volume"] for i in data["ohlcv"]])[-20:] # Last 20 days for CYBN
            mnmd_volumes = np.array([i["MNMD"]["volume"] for i in data["ohlcv"]])[-20:] # Last 20 days for MNMD
            
            # Ensure we have enough data points
            if len(cybn_volumes) < 20 or len(mnmd_volumes) < 20:
                log("Not enough data")
                return TargetAllocation({})
                
            # Calculate the correlation coefficient between CYBN and MNMD volumes
            correlation_coefficient = np.corrcoef(cybn_volumes, mnmd_volumes)[0, 1]
            log(f"Volume Correlation: {correlation_coefficient}")
            
            # Initialize stake in CYBN based on correlation
            # For example, invest in CYBN if the volumes are positively correlated above a threshold
            if correlation_coefficient > 0.5: # arbitrary threshold
                cybn_stake = 1.0  # Full investment in CYBN
            else:
                cybn_stake = 0  # No investment in CYBN
            
            return TargetAllocation({"CYBN": cybn_stake})
        except Exception as e:
            log(f"Error calculating allocation: {str(e)}")
            return TargetAllocation({})