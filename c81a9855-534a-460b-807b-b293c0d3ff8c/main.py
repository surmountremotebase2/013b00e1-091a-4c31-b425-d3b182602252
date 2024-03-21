# Import the necessary classes and functions from the Surmount package
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, SMA, MACD, MFI, OBV
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Set the ticker for Cybin; adjust accordingly if Cybin's ticker is different
        self.ticker = "CYBN"
        # Specify the data required for the indicators
        self.data_list = []

    @property
    def assets(self):
        # The assets we're interested in (Cybin in this case)
        return [self.ticker]

    @property
    def interval(self):
        # We'll look at daily intervals to catch broader market movements
        return "1day"

    @property
    def data(self):
        # Data requirements should match the indicators used. This is placeholder.
        return self.data_list

    def run(self, data):
        # Implement strategy to decide on buying (1), holding (0), or selling (-1)

        # Retrieve historical data for Cybin
        d = data["ohlcv"]

        # Initialize allocation and historical data analysis
        allocation = 0

        if len(d) >= 20:  # Ensure we have enough data points
            # Calculate technical indicators to guide our trading strategy
            rsi = RSI(self.ticker, d, length=14)
            ema_short = EMA(self.ticker, d, length=9)
            ema_long = EMA(self.ticker, d, length=26)
            obv = OBV(self.ticker, d)

            # Latest indicator values
            latest_rsi = rsi[-1]
            latest_ema_short = ema_short[-1]
            latest_ema_long = ema_long[-1]
            latest_obv = obv[-1]
            previous_obv = obv[-2]

            # Strategy:
            # Buy if RSI < 30 (oversold), short EMA crosses above long EMA, and OBV is increasing
            if latest_rsi < 30 and latest_ema_short > latest_ema_long and latest_obv > previous_obv:
                allocation = 1  # Indicates a buy action

            # Sell if RSI > 70 (overbought), short EMA crosses below long EMA, or OBV is decreasing
            elif latest_rsi > 70 or latest_ema_short < latest_ema_long or latest_obv < previous_obv:
                allocation = -1  # Indicates a sell/short action

        # Construct TargetAllocation object
        # Note: The platform likely requires normalized allocations (0 to 1), revise the allocation accordingly
        # This example assigns a full position (1) or no position (0) to simplify the logic
        allocation_dict = {self.ticker: max(0, allocation)}
        return TargetAllocation(allocation_dict)