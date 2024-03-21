from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["CYBN"]
        self.ema_short_period = 12
        self.ema_long_period = 26
        self.atr_period = 14
        self.stop_loss_multiplier = 3  # How many ATRs away to set the stop loss
        self.recent_trades = []  # To keep track of buy signals to enforce tax efficiency

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        ohlcv_data = data["ohlcv"]
        current_price = ohlcv_data[-1]["CYBN"]["close"]

        ema_short = EMA("CYBN", ohlcv_data, self.ema_short_period)
        ema_long = EMA("CYBN", ohlcv_data, self.ema_long_period)
        atr = ATR("CYBN", ohlcv_data, self.atr_period)

        cybn_stake = 0

        if len(ema_short) == 0 or len(ema_long) == 0 or len(atr) == 0:
            log("Not enough data to calculate indicators")
            return TargetAllocation({"CYBN": cybn_stake})

        # Trend determination
        is_uptrend = ema_short[-1] > ema_long[-1]

        # Stop loss calculation based on the most recent ATR
        stop_loss_level = current_price - (atr[-1] * self.stop_loss_multiplier)

        # Check if there is a valid buy signal
        if is_uptrend and (len(self.recent_trades) == 0 or self.recent_trades[-1]["action"] != "buy"):
            cybn_stake = 1  # 100% allocation
            self.recent_trades.append({"action": "buy", "price": current_price})
            log("Buying CYBN at best possible price")

        # Incorporating basic tax efficiency by avoiding selling if recently bought
        elif not is_uptrend and len(self.recent_trades) > 0 and self.recent_trades[-1]["action"] == "buy":
            last_buy_price = self.recent_trades[-1]["price"]
            # Check stop-loss condition and holdings duration for tax efficiency
            if current_price <= stop_loss_level or (current_price > last_buy_price and self.hold_long_enough()):
                cybn_stake = 0  # No allocation
                self.recent_trades.append({"action": "sell", "price": current_price})
                log("Selling CYBN aiming for a better price, enforcing stop-loss, or for tax efficiency")

        else:
            log("No trade signal as per the defined strategy")

        return TargetAllocation({"CYBN": cybn_stake})

    def hold_long_enough(self):
        # Simplification: assuming "long enough" means a predetermined period, e.g., over 30 days for this example
        # In reality, this should compare with actual tax policy periods, e.g., 1 year for long-term capital gains
        return len(self.recent_trades) > 365  # This is a mock-up function for demonstration. Implement accordingly.