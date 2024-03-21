from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, ATR
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["CYBN"]  # Add more penny stock tickers as desired
        self.ema_length_short = 10
        self.ema_length_long = 50
        self.atr_length = 14
        self.risk_multiplier = 1.5  # ATR risk multiplier for stop loss

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            ohlcv_data = data["ohlcv"]
            ema_short = EMA(ticker, ohlcv_data, self.ema_length_short)
            ema_long = EMA(ticker, ohlcv_data, self.ema_length_long)
            atr = ATR(ticker, ohlcv_data, self.atr_length)

            #if len(ema_short) == 0 or len(ema_long) == 0 or len(atr) == 0:
            #    log(f"Insufficient data for trading: {ticker}")
            #    allocation_dict[ticker] = 0
            #    continue

            current_price = ohlcv_data[-1][ticker]["close"]
            ema_short_latest = ema_short[-1]
            ema_long_latest = ema_long[-1]
            atr_latest = atr[-1]

            stop_loss = current_price - (atr_latest * self.risk_multiplier)

            # Entry condition: if short-term EMA crosses above long-term EMA
            if ema_short_latest > ema_long_latest:
                # Only execute buy if we haven't already entered the position
                if "cash" in data["holdings"] and data["holdings"]["cash"] > 0:
                    log(f"Buying {ticker} at {current_price}, setting stop loss at {stop_loss}")
                    allocation_dict[ticker] = 1  
                else:
                    allocation_dict[ticker] = 0  
            else:
                # If the conditions are not met, keep the cash (no position in the asset)
                allocation_dict[ticker] = 0  

        return TargetAllocation(allocation_dict)