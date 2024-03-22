from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Ticker for the asset we're trading and the asset we're observing
        self.trade_ticker = "CYBN"
        self.observe_ticker = "MNMD"
        # How much of our portfolio to allocate to our trade_ticker
        self.trading_allocation = 1.0
        # Stop Loss Percentage (e.g., 0.05 for 5%)
        self.stop_loss_percentage = 0.35
        # Keep track of buying price for calculating stop loss
        self.buying_price = None

    @property
    def assets(self):
        # We're interested in both assets, although we're only trading one
        return [self.trade_ticker, self.observe_ticker]

    @property
    def interval(self):
        # Using daily data for decision making
        return "1day"

    def run(self, data):
        # Initialize allocation with no position
        allocation_dict = {self.trade_ticker: 0}

        # Calculate the 10-day simple moving average for MNMD
        sma_mnmd = SMA(self.observe_ticker, data["ohlcv"], 10)

        if sma_mnmd is None or len(sma_mnmd) < 10:
            # Not enough data to make a decision
            return TargetAllocation(allocation_dict)

        # Latest closing prices for MNMD and CYBN
        latest_close_mnmd = data["ohlcv"][-1][self.observe_ticker]["close"]
        latest_close_cybn = data["ohlcv"][-1][self.trade_ticker]["close"]

        if self.buying_price is None and latest_close_mnmd > sma_mnmd[-1]:
            # If MNMD's price is above its SMA, and we haven't bought CYBN yet, buy
            allocation_dict[self.trade_ticker] = self.trading_allocation
            self.buying_price = latest_close_cybn
        elif self.buying_price is not None:
            # If we have bought CYBN, check for stop loss or take profit conditions
            if (latest_close_cybn < self.buying_price * (1 - self.stop_loss_percentage)):
                # If current price is below the stop loss threshold, sell
                allocation_dict[self.trade_ticker] = 0
                self.buying_price = None  # Reset buying price
            else:
                # Keep the position if none of the sell conditions are met
                allocation_dict[self.trade_ticker] = self.trading_allocation

        return TargetAllocation(allocation_dict)