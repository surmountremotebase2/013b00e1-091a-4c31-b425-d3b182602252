from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, VWAP
from surmount.logging import log
from surmount.data import Asset
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        # Assuming penny stocks are those priced below $5; you can adjust this value.
        self.max_price = 5  
        # Customize this list with the tickers of your interest or dynamically fetch penny stocks tickers
        self.tickers = ["PENNY1", "PENNY2", "PENNY3", "PENNY4"]
        self.data_list = [Asset(i) for i in self.tickers]

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            asset_data = data["ohlcv"]

            # Ensure we have enough data points for analysis
            if len(asset_data) < 35:  # 35 days as an arbitrary choice; adjust based on your indicators.
                continue

            # Filter based on price
            current_price = asset_data[-1][ticker]["close"]
            if current_price > self.max_price:
                continue

            # Volume Weighted Average Price (VWAP) for liquidity assessment
            vwap_values = VWAP(ticker, asset_data, 20)  # 20 days as an example

            # MACD for momentum
            macd_data = MACD(ticker, asset_data, fast=12, slow=26)
            macd_line = macd_data['MACD']
            signal_line = macd_data['signal']

            # Conditions for picking the stock:
            # - Current price is less than the VWAP (indicates potential undervalued status)
            # - MACD line is above the signal line (positive momentum)
            if current_price < vwap_values[-1] and macd_line[-1] > signal_line[-1]:
                allocation_dict[ticker] = 1.0 / len(self.tickers)  # Equal distribution among selected stocks
            else:
                allocation_dict[ticker] = 0

        # Return target allocation with equal weightage to selected tickers
        return TargetAllocation(allocation_dict)