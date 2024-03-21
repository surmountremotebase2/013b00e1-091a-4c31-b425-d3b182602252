from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Initialize with the target ticker
        self.ticker = "CYBN"
        # Start with an assumption of not being invested
        self.already_invested = False
        # Initialize the ATR period for volatility estimation
        self.atr_period = 14
        # EMA periods for trend following (fast and slow for trend confirmation)
        self.ema_fast_period = 50
        self.ema_slow_period = 200
        # The stop loss factor determines how tight the stop loss is.
        # A higher factor means we are allowing more room for the price to move
        self.stop_loss_factor = 3
        # Record the buy price for calculating holding duration
        self.buy_price = 0

    @property
    def interval(self):
        # Daily interval for long-term trend following
        return "1day"

    @property
    def assets(self):
        # Only interested in CYBN for this strategy
        return [self.ticker]

    def run(self, data):
        # Extract closing price and calculate indicators
        close_prices = [i[self.ticker]["close"] for i in data["ohlcv"]]
        ema_fast = EMA(self.ticker, data["ohlcv"], self.ema_fast_period)
        ema_slow = EMA(self.ticker, data["ohlcv"], self.ema_slow_period)
        atr = ATR(self.ticker, data["ohlcv"], self.atr_period)

        # Checking if we have enough data to proceed
        if not ema_fast or not ema_slow or not atr:
            return TargetAllocation({})

        # Default to no allocation
        allocation = 0

        # Calculate current price and stop loss price
        current_price = close_prices[-1]
        stop_loss_price = self.buy_price - (atr[-1] * self.stop_loss_factor)

        # Determine if we should enter a position
        if ema_fast[-1] > ema_slow[-1] and not self.already_invested:
            log("Entering a position in CYBN.")
            allocation = 1  # Max allocation to CYBN
            self.already_invested = True
            self.buy_price = current_price

        # Determine if we should exit the position
        # Checking stop loss or if we've held for over a year for tax efficiency
        elif self.already_invested:
            if current_price <= stop_loss_price or data["ohlcv"][-1][self.ticker]["date"] - self.buy_price >= 365:
                log("Exiting the position in CYBN.")
                allocation = 0
                self.already_invested = False
                self.buy_price = 0  # Reset buy price

        # If still invested and there's no condition to sell, hold the position
        elif self.already_invested:
            allocation = 1

        return TargetAllocation({self.ticker: allocation})