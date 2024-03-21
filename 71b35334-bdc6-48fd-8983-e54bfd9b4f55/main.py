from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA, EMA
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    """
    This strategy aims to maximize profits on penny stocks that are expected to grow. It utilizes
    price momentum indicated by the Exponential Moving Average (EMA) crossover as a buy signal,
    supplemented by the Relative Strength Index (RSI) to identify overbought conditions.
    A simple moving average (SMA) acts as a dynamic stop-loss level to mitigate risks.
    """

    def __init__(self):
        # Define the penny stock tickers you're interested in.
        self.tickers = ["CYBN"]
        self.lookback_window = 30  # Lookback period for indicators.

    @property
    def interval(self):
        return "1day"  # Daily interval to catch overall trends without too much noise.

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}

        for ticker in self.tickers:
            # Retrieve historical closing prices for each ticker.
            close_prices = data["ohlcv"][ticker]["close"]

            # Calculate EMA for two different periods to determine the crossover.
            ema_short = EMA(ticker, data["ohlcv"], length=9)
            ema_long = EMA(ticker, data["ohlcv"], length=21)

            # Calculate RSI to check if the stock is overbought.
            rsi = RSI(ticker, data["ohlcv"], length=14)

            # Define the stop loss level as the recent SMA.
            stop_loss_level = SMA(ticker, data["ohlcv"], length=50)[-1]

            # Initial allocation is zero for each ticker.
            allocation = 0

            # Check if the short EMA is above the long EMA indicating an upward price momentum.
            if ema_short[-1] > ema_long[-1]:
                # Check if the RSI is not indicating an overbought condition (RSI below 70).
                if rsi[-1] < 70:
                    # Position is taken if the conditions are met, setting allocation to a fraction of the portfolio.
                    allocation = 0.2

            # Adjust the allocation to zero if the current price is below stop loss level.
            if close_prices[-1] < stop_loss_level:
                allocation = 0

            allocation_dict[ticker] = allocation

        log(f"Allocations: {allocation_dict}")
        return TargetAllocation(allocation_dict)