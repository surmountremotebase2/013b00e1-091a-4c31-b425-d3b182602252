from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, MACD, RSI, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # We're only interested in CYBN for this strategy.
        self.ticker = "CYBN"
        # Initial variables for MACD crossover and minimum holding period
        self.entry_macd_signal_crossed = False
        self.exit_macd_signal_crossed = False
        self.holding_start_date = None
        self.initial_stop_loss = None

    @property
    def assets(self):
        # Specifies that our strategy is only concerned with CYBN.
        return [self.ticker]

    @property
    def interval(self):
        # Using '1day' interval for this strategy to focus on daily trends.
        return "1day"

    def run(self, data):
        # Retrieve the close prices, MACD indicator results, RSI, and ATR for stop-loss calculation.
        prices = [d[self.ticker]["close"] for d in data["ohlcv"]]
        macd_indicator = MACD(self.ticker, data["ohlcv"], fast=12, slow=26)
        rsi = RSI(self.ticker, data["ohlcv"], length=14)
        atr = ATR(self.ticker, data["ohlcv"], length=14)

        # Define stake in CYBN. By default, do not invest.
        cybn_stake = 0

        if not prices or macd_indicator is None or rsi is None or atr is None:
            return TargetAllocation({})

        # Check if MACD line crossed above the signal line for a buy signal.
        if not self.entry_macd_signal_crossed and macd_indicator["MACD"][-1] > macd_indicator["signal"][-1]:
            self.entry_macd_signal_crossed = True
            self.holding_start_date = data["ohlcv"][-1][self.ticker]["date"]
            self.initial_stop_loss = prices[-1] - (2 * atr[-1])  # Set initial stop loss as 2x the ATR from the entry price.
            log(f"Entering position on {self.holding_start_date}, Stop Loss: {self.initial_stop_loss}")
            cybn_stake = 1  # Full investment in CYBN

        # Check if already entered and one year has passed
        if self.entry_macd_signal_crossed:
            one_year_later = str(int(self.holding_start_date.split("-")[0]) + 1) + self.holding_start_date[4:]
            current_date = data["ohlcv"][-1][self.ticker]["date"]
            # Allow exit only if more than a year has passed and MACD crosses below signal or price drops below the stop loss.
            if current_date >= one_year_later:
                if macd_indicator["MACD"][-1] < macd_indicator["signal"][-1]:
                    self.exit_macd_signal_crossed = True
                    log(f"Exiting position on {current_date}, MACD Signal Exit")
                    cybn_stake = 0  # Sell CYBN
                elif prices[-1] < self.initial_stop_loss:
                    log(f"Exiting position on {current_date}, Stop Loss Hit")
                    cybn_stake = 0  # Sell CYBN due to stop loss
                
        # If investment conditions are met, allocate accordingly, else maintain previous position (or none if not yet entered).
        if cybn_stake == 1:
            return TargetAllocation({self.ticker: 1})  # Invest completely in CYBN
        else:
            return TargetAllocation({})  # Hold or exit the investment