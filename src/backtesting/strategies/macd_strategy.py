from zipline.api import order, schedule_function, date_rules, time_rules
from .base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    def initialize(self, context):
        """
        Initialize MACD strategy parameters.
        """
        context.short_window = 12
        context.long_window = 26
        context.signal_window = 9

        # Schedule the rebalance function
        schedule_function(self.rebalance, date_rules.every_day(), time_rules.market_close())

    def rebalance(self, context, data):
        """
        Rebalance portfolio based on MACD signals.
        """
        for asset in context.portfolio.positions:
            # Calculate MACD and signal line
            macd = data.history(asset, "close", context.short_window, "1d").mean() - \
                   data.history(asset, "close", context.long_window, "1d").mean()
            signal = data.history(asset, "close", context.signal_window, "1d").mean()

            # Generate trading signals
            if macd > signal:
                order(asset, 10)  # Buy signal
            elif macd < signal:
                order(asset, -10)  # Sell signal
                