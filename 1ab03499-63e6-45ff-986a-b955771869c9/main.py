from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # CYBN is the asset we are interested in trading
        self.tickers = ["CYBN"]

    @property
    def interval(self):
        # Setting the data interval to '1day' for daily trading signals
        return "1day"

    @property
    def assets(self):
        # Specifying the assets we are trading
        return self.tickers

    def run(self, data):
        # Access the closing prices for CYBN from the provided data
        close_prices = [i["CYBN"]["close"] for i in data["ohlcv"]]

        # Calculate the short-term and long-term EMAs for CYBN
        short_ema = EMA("CYBN", data["ohlcv"], length=12)
        long_ema = EMA("CYBN", data["ohlcv"], length=26)

        # Calculate the RSI for CYBN
        rsi = RSI("CYBN", data["ohlcv"], length=14)

        # Calculate the SMA as a dynamic stop-loss level
        sma_stop_loss = SMA("CYBN", data["ohlcv"], length=50)

        # Initial investment decision is to hold no position
        cybn_stake = 0

        if len(close_prices) > 0:
            current_price = close_prices[-1]

            # Check if the short-term EMA crosses above the long-term EMA indicating a buy signal,
            # but also ensure the RSI is not indicating an overbought condition (< 70)
            if short_ema[-1] > long_ema[-1] and rsi[-1] < 70:
                cybn_stake = 1  # Full investment in CYBN

            # Implement the dynamic stop-loss using SMA
            if current_price < sma_stop_loss[-1]:
                cybn_stake = 0  # Sell CYBN to stop loss

        # Log the investment decision for debugging purposes
        log(f"Allocating {cybn_stake * 100}% of the portfolio to CYBN.")

        # Return the target allocation for CYBN
        return TargetAllocation({"CYBN": cybn_stake})