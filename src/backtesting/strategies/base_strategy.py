class BaseStrategy:
    def initialize(self, context):
        """
        Initialize the strategy parameters.
        """
        pass

    def handle_data(self, context, data):
        """
        Handle data at each step of the backtest.
        """
        pass

    def rebalance(self, context, data):
        """
        Define trading logic for rebalancing.
        """
        pass
    