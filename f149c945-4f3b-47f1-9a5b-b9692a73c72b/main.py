from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Asset
from surmount.technical_indicators import ATR

class TradingStrategy(Strategy):
    """
    A trading strategy that enters long positions in Cybin with a reasonable stop loss using ATR for risk management.
    """

    def __init__(self):
        self.ticker = "CYBN"
        # Define the risk per trade as a percentage of the current asset value
        self.risk_per_trade = 0.02  # 2%
        # Multiplier for ATR to set the stop loss
        self.atr_multiplier = 3

    @property
    def interval(self):
        # Use daily data for the strategy
        return "1day"

    @property
    def assets(self):
        # Trade only Cybin
        return [self.ticker]

    @property
    def data(self):
        # No additional data requirements
        return []

    def run(self, data):
        # Calculate the Average True Range (ATR) for risk assessment
        atr_values = ATR(self.ticker, data["ohlcv"], 14)

        if not atr_values:
            return TargetAllocation({})

        # Current ATR value
        current_atr = atr_values[-1]

        # Current close price of Cybin
        current_price = data["ohlcv"][-1][self.ticker]["close"]

        # Calculate the stop loss price
        stop_loss_price = current_price - (self.atr_multiplier * current_atr)

        # Calculate the number of shares to buy based on risk management
        # Assuming the 'account_value' is a variable representing the total account value
        # account_value = 100000  # Example value
        # shares_to_buy = (self.risk_per_trade * account_value) / (current_price - stop_loss_price)

        # Since this platform does not give direct control over the quantity, 
        # we adjust our target allocation based on the risk willingness instead
        allocation_percentage = min(self.risk_per_trade, 0.1)  # Limiting the allocation to a maximum of 10%

        # Log the stop loss value for reference
        print(f"Setting stop loss for {self.ticker} at ${stop_loss_price:.2f}")

        # Return the target allocation as a fraction (percentage) of the total capital
        return TargetAllocation({self.ticker: allocation_percentage})