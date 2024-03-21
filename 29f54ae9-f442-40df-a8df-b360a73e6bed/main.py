from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, SMA, MACD, ATR
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Penny stocks including CYBN
        self.tickers = ["CYBN"]
        # Add more penny stocks as per your research and risk appetite

        # Stop-loss percentage (adjust according to your risk tolerance)
        self.stop_loss_percentage = 0.10  # 10% stop loss
        # Take-profit percentage
        self.take_profit_percentage = 0.20  # 20% profit target

    @property
    def interval(self):
        # Choosing '1day' for daily market analysis, could be finer like '1hour' or '30min' for more active trading
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # We only need OHLCV data for this strategy
        return []

    def run(self, data):
        allocations = {}
        holdings = data["holdings"]
        ohlcv = data["ohlcv"]

        for ticker in self.tickers:
            current_price = ohlcv[-1][ticker]['close']

            if ticker in holdings:
                buy_price = holdings[ticker]["buy_price"]
                # Calculate stop loss and take profit prices
                stop_loss_price = buy_price * (1 - self.stop_loss_percentage)
                take_profit_price = buy_price * (1 + self.take_profit_percentage)

                if current_price <= stop_loss_price:
                    log(f"Selling {ticker}, hit stop loss")
                    allocations[ticker] = 0  # Sell
                elif current_price >= take_profit_price:
                    log(f"Selling {ticker}, hit take profit")
                    allocations[ticker] = 0  # Sell
                else:
                    allocations[ticker] = 1  # Hold
            else:
                # Use a combination of indicators like MACD and RSI to find the best buy signals
                macd_indicator = MACD(ticker, ohlcv, fast=12, slow=26)
                rsi_indicator = RSI(ticker, ohlcv, length=14)

                if len(macd_indicator['MACD']) > 0 and len(rsi_indicator) > 0:
                    # Check for MACD crossover and RSI oversold condition
                    macd_current = macd_indicator['MACD'][-1]
                    macd_signal = macd_indicator['signal'][-1]
                    rsi_current = rsi_indicator[-1]

                    if macd_current > macd_signal and rsi_current < 30:
                        log(f"Buying {ticker}, MACD crossover and RSI oversold")
                        allocations[ticker] = 1  # Buy a full position
                    else:
                        allocations[ticker] = 0  # Do not buy
                else:
                    # Not enough data to make a decision
                    allocations[ticker] = 0

        return TargetAllocation(allocations)