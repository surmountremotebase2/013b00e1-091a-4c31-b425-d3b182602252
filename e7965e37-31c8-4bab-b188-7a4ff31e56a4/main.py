from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI
from surmount.logging import log
from surmount.data import Asset

# Define a trading strategy that invests in biotech, including CYBN, based on technical indicators.
class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers of biotech stocks. Including CYBN.
        self.tickers = ["CYBN"]
    
    @property
    def interval(self):
        # Use daily data for the analysis.
        return "1day"
    
    @property
    def assets(self):
        # Return the list of tickers the strategy will analyze and potentially trade.
        return self.tickers
    
    @property
    def data(self):
        # In this example, we won't use additional data sources.
        return []
    
    def run(self, data):
        allocation_dict = {}
        
        # Iterate through each ticker to calculate indicators and decide on allocation.
        for ticker in self.tickers:
            # Compute the 50-day Exponential Moving Average (EMA) and the Relative Strength Index (RSI).
            ema50 = EMA(ticker, data["ohlcv"], length=50)
            rsi14 = RSI(ticker, data["ohlcv"], length=14)
            
            # Ensure we have enough data to calculate both EMA and RSI.
            if ema50 is not None and rsi14 is not None:
                # Apply investment decision logic:
                # - Enter or increase position if EMA is trending up and RSI < 70 signaling not overbought.
                if rsi14[-1] < 70 and ema50[-1] > ema50[-2]:
                    allocation_dict[ticker] = 1 / len(self.tickers)
                else:
                    allocation_dict[ticker] = 0
            else:
                # Log an error if we cannot compute the EMA or RSI.
                log(f"Unable to compute indicators for {ticker}.")
                allocation_dict[ticker] = 0
        
        # Return the target allocation for each ticker.
        return TargetAllocation(allocation_dict)