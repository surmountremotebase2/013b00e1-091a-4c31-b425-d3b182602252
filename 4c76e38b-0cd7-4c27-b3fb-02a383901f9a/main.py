from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Tickers for CYBN and MNMD
        self.cybn_ticker = "CYBN"
        self.mnmd_ticker = "MNMD"
        self.entry_price = None  # To keep track of entry price for stop loss calculation
        self.stop_loss_percent = 0.1  # 10% stop loss

    @property
    def assets(self):
        # This strategy only trades CYBN but uses indicators from MNMD to decide
        return [self.cybn_ticker, self.mnmd_ticker]

    @property
    def interval(self):
        # Using daily data for this strategy
        return "1day"

    def run(self, data):
        mnmd_rsi = RSI(self.mnmd_ticker, data["ohlcv"], 14)  # 14-day RSI for MNMD
        mnmd_macd = MACD(self.mnmd_ticker, data["ohlcv"], 12, 26)  # MACD for MNMD using the standard 12, 26 periods

        cybn_holdings = data["holdings"][self.cybn_ticker]  # Current holdings for CYBN
        cybn_current_price = data["ohlcv"][-1][self.cybn_ticker]["close"]  # Current price for CYBN

        allocation_dict = {self.cybn_ticker: 0}  # Default to no allocation

        # Buy Condition: Enter if RSI < 30 (Oversold) and MACD line crosses above signal line
        if mnmd_rsi[-1] < 30 and mnmd_macd["MACD"][-1] > mnmd_macd["signal"][-1]:
            allocation_dict[self.cybn_ticker] = 1.0  # Allocate 100% to CYBN
            self.entry_price = cybn_current_price  # Set entry price for stop loss calculation

        # Stop Loss Condition
        if self.entry_price and cybn_current_price < self.entry_price * (1 - self.stop_loss_percent):
            log(f"Activating stop loss for {self.cybn_ticker}. Current Price: {cybn_current_price}, Entry Price: {self.entry_price}")
            allocation_dict[self.cybn_ticker] = 0  # Sell CYBN to stop loss

        # Sell Condition: Exit if RSI > 70 (Overbought) or MACD line crosses below signal line
        if cybn_holdings > 0 and (mnmd_rsi[-1] > 70 or mnmd_macd["MACD"][-1] < mnmd_macd["signal"][-1]):
            allocation_dict[self.cybn_ticker] = 0  # Sell CYBN to exit position

        return TargetAllocation(allocation_dict)