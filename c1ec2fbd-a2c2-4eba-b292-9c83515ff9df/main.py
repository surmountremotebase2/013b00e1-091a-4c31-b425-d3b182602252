from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker we're interested in
        self.ticker = "CYBN"
        # Define the multiplier for the ATR-based stop loss
        self.atr_multiplier = 2

    @property
    def assets(self):
        # We're only trading CYBN
        return [self.ticker]

    @property
    def interval(self):
        # Daily interval for trading signals
        return "1day"

    def run(self, data):
        # Initialize stake in CYBN to 0
        cybn_stake = 0
        
        # Calculate ATR for CYBN for risk management (stop loss)
        atr_values = ATR(self.ticker, data["ohlcv"], length=14)  # Using 14-day ATR

        if len(atr_values) > 0:
            current_atr = atr_values[-1]
            last_close_price = data["ohlcv"][-1][self.ticker]['close']
            
            # Calculate the stop loss price
            stop_loss_price = last_close_price - (self.atr_multiplier * current_atr)

            # Log the calculated stop loss price for information
            log(f"Stop loss for {self.ticker} set at: {stop_loss_price:.2f}")

            # Example logic for entering a position.
            # This does not directly execute trades but sets the desired allocation.
            # Actual trade execution depends on integration with your brokerage or simulation.
            # Here we simply decide to take a long position. You should add your entry logic.
            cybn_stake = 1  # Indicating a full investment in the asset of interest

            # Note: To actively enforce the stop loss in live trading, external execution logic is needed.
        
        return TargetAllocation({self.ticker: cybn_stake})