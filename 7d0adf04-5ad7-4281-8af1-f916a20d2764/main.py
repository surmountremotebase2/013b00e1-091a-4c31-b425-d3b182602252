from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA, EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "CYBN"
        self.entry_rsi_threshold = 30  # RSI level to consider entry
        self.exit_rsi_threshold = 70  # RSI level to consider exit
        self.stop_loss_percent = 0.10  # 10% stop loss
        self.holding_period = 30  # Minimum holding period in days for tax efficiency
        self.last_buy_price = None  # Track last buy price
        self.buy_date = None  # Track when the stock was bought

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        ohlcv = data["ohlcv"]
        current_price = ohlcv[-1][self.ticker]["close"]
        current_date = ohlcv[-1][self.ticker]["date"]
        rsi = RSI(self.ticker, ohlcv, length=14)

        allocation_dict = {self.ticker: 0}  # Default to no allocation

        # Check if we hold the stock and meet the minimum holding period for tax efficiency
        if self.last_buy_price and self.buy_date:
            days_held = (current_date - self.buy_date).days
            loss = self.last_buy_price * self.stop_loss_percent

            if (current_price <= self.last_buy_price - loss) or (rsi[-1] > self.exit_rsi_threshold and days_held >= self.holding_period):
                log(f"Selling {self.ticker} for stop loss or profit booking after holding for {days_held} days")
                allocation_dict[self.ticker] = 0  # Sell
                self.last_buy_price = None
                self.buy_date = None
            else:
                allocation_dict[self.ticker] = 1  # Hold
        # Check entry condition
        elif rsi[-1] < self.entry_rsi_threshold:
            log(f"Buying {self.ticker} at RSI={rsi[-1]}")
            allocation_dict[self.ticker] = 1  # Buy
            self.last_buy_price = current_price
            self.buy_date = current_date

        return TargetAllocation(allocation_dict)