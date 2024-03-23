from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the main asset to trade and auxiliary assets for analysis
        self.main_asset = "QCOM"
        self.aux_assets = ["IBM", "HPQ", "DELL", "GOOGL", "AVGO", "TXN", "NOK"]
        self.initial_investment = False  # To check if Qualcomm has been purchased

    @property
    def assets(self):
        # List all the assets involved in the strategy
        return [self.main_asset] + self.aux_assets

    @property
    def interval(self):
        # Set the data interval for analysis
        return "1day"

    def run(self, data):
        # Current strategy does not require additional data inputs
        allocation_dict = {self.main_asset: 0}  # Default allocation

        qcom_data = data["ohlcv"]
        qcom_close = qcom_data[-1][self.main_asset]["close"]
        qcom_sma = SMA(self.main_asset, qcom_data, 20)[-1]  # 20-day SMA for Qualcomm

        if self.initial_investment:
            # If Qualcomm has been purchased, check for stop-loss or take-profit conditions
            purchase_price = self.current_holdings[self.main_asset]["averagePrice"]
            if qcom_close <= purchase_price * 0.95:  # Stop-loss condition
                log("Selling QCOM to stop further loss.")
                allocation_dict[self.main_asset] = 0
            elif qcom_close >= purchase_price * 1.10:  # Take-profit condition
                log("Selling QCOM to secure profits.")
                allocation_dict[self.main_asset] = 0
            else:
                # Maintain the position if no thresholds are met
                allocation_dict[self.main_asset] = self.current_holdings[self.main_asset]["quantity"]
        else:
            # Check if Qualcomm is a good buy based on its price compared to its SMA
            if qcom_close > qcom_sma:
                log("Buying QCOM based on SMA strategy.")
                allocation_dict[self.main_asset] = 1
                self.initial_investment = True  # Indicate that QCOM has been purchased

        return TargetAllocation(allocation_dict)