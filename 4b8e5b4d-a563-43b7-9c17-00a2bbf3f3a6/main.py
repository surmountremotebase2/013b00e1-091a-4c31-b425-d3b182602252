from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.buy_price = None  # Tracks the buying price of CYBN
        self.stop_loss = 0.10  # Stop-loss threshold (5% drop)
        self.take_profit = 0.15  # Take profit threshold (10% increase)
        self.tickers = ["CYBN", "MNMD"]

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        # Initialize allocation for CYBN to 0 (no current investment)
        allocation_dict = {"CYBN": 0}

        # Check if there's sufficient data for MNMD to compute the SMA
        if len(data["ohlcv"]) > 10:
            # Obtain the last 10 days of closing prices for MNMD and compute its SMA
            mnmd_closes = [i["MNMD"]["close"] for i in data["ohlcv"][-10:]]
            mnmd_sma = SMA("MNMD", data["ohlcv"], 10)[-1]

            # Get the latest closing price for CYBN and MNMD
            cybn_latest_close = data["ohlcv"][-1]["CYBN"]["close"]
            mnmd_latest_close = data["ohlcv"][-1]["MNMD"]["close"]

            # Check buy condition: MNMD's price is above its SMA and CYBN is not purchased yet
            if mnmd_latest_close > mnmd_sma and self.buy_price is None:
                self.buy_price = cybn_latest_close
                allocation_dict["CYBN"] = 1  # Assign 100% of the portfolio to CYBN

            # If CYBN is already purchased, check for stop loss or take profit conditions
            elif self.buy_price is not None:
                price_drop = (self.buy_price - cybn_latest_close) / self.buy_price
                price_gain = (cybn_latest_close - self.buy_price) / self.buy_price

                if price_drop >= self.stop_loss:
                    log("Selling CYBN due to stop loss")
                    self.buy_price = None  # Reset buying price
                elif price_gain >= self.take_profit:
                    log("Selling CYBN to take profit")
                    self.buy_price = None  # Reset buying price
                else:
                    # Hold the position if neither stop loss nor take profit conditions are met
                    allocation_dict["CYBN"] = 1

        return TargetAllocation(allocation_dict)