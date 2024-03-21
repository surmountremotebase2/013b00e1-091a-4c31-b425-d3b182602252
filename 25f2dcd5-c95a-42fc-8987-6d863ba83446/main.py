from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import BB
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.asset = "CYBN"  # Focusing on Cybin Inc.
        self.entry_buffer = 1.02  # Buffer for entry above the upper band
        self.exit_buffer = 0.98  # Buffer for stop loss below the lower band
        # Initial stop loss can be set more strategically based on historical data analysis
        self.initial_stop_loss = None  # Dynamically updated based on entry

    @property
    def assets(self):
        return [self.asset]

    @property
    def interval(self):
        # Daily checks to follow the "hold for at least 1 year" guideline more closely
        return "1day"

    def run(self, data):
        holdings = data["holdings"]
        ohlcv_data = data["ohlcv"]
        
        # Ensure there is enough data for BB calculations
        if len(ohlcv_data) < 20:
            return TargetAllocation({})

        # Calculate Bollinger Bands
        bollinger_bands = BB(self.asset, ohlcv_data, 20, 2)  # Using 20-day MA with 2 std deviations
        
        current_price = ohlcv_data[-1][self.asset]['close']
        upper_band = bollinger_bands['upper'][-1]
        lower_band = bollinger_bands['lower'][-1]

        cybn_stake = 0

        # Entry condition: Price breaks above the upper band considering the entry buffer
        if current_price > upper_band * self.entry_buffer:
            log(f"Entering long position for {self.asset}")
            if self.initial_stop_loss is None:
                self.initial_stop_loss = lower_band * self.exit_buffer  # Setting initial stop-loss
            
            # Determine the amount to pyramid based on existing holdings
            # Simple Strategy: Increase position by 10% if already holding
            cybn_stake = 0.1 if holdings.get(self.asset, 0) > 0 else 1

        # Exit condition: Price falls below adjusted stop-loss level
        elif current_price < self.initial_stop_loss:
            log(f"Exiting position for {self.asset} due to stop-loss")
            cybn_stake = 0  # Sell off the position

        return TargetAllocation({self.asset: cybn_stake})