from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV
from datetime import datetime, timedelta

class TradingStrategy(Strategy):
    def __init__(self):
        # Asset to trade
        self.tickers = ["CYBN"]
        # Historical data window for calculating volatility
        self.lookback_period = 252  # Approximately 1 year of trading days
        # Set a percentage of volatility for stop loss; adjust based on risk appetite
        self.stop_loss_multiplier = 2
        # Initialize with no stop loss
        self.stop_loss = None
        self.investment_start_date = None

    @property
    def interval(self):
        # Daily data to review trends over time
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # Requesting historical OHLCV data for the lookback period +1 for the stop loss calculation
        return [OHLCV(ticker, self.interval, self.lookback_period + 1) for ticker in self.tickers]

    def run(self, data):
        # Sample date format '2023-01-01'; Adjust based on actual data format
        today = datetime.strptime(data['ohlcv'][0]['CYBN']['date'], '%Y-%m-%d')
        if not self.investment_start_date:
            self.investment_start_date = today

        # Check if we have held for at least 1 year
        if today - self.investment_start_date < timedelta(days=365):
            return TargetAllocation({"CYBN": 1.0})  # Continuing to hold
        
        # Calculate stop loss on the first day of investment
        if self.stop_loss is None:
            close_prices = [day["CYBN"]["close"] for day in data['ohlcv']]
            daily_returns = [((close_prices[i] - close_prices[i - 1]) / close_prices[i - 1]) for i in range(1, len(close_prices))]
            volatility = stdev(daily_returns)
            current_price = close_prices[-1]
            self.stop_loss = current_price - (volatility * self.stop_loss_multiplier)
        
        # Check if current price breaks the stop loss
        current_price = data['ohlcv'][-1]["CYBN"]["close"]
        if current_price <= self.stop_loss:
            # Sell the position
            return TargetAllocation({"CYBN": 0})
        
        # If none of the above conditions are met, hold the position
        return TargetAllocation({"CYBN": 1.0})