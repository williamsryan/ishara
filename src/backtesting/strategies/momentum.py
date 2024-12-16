import backtrader as bt

class MomentumStrategy(bt.Strategy):
    params = (("lookback", 20), ("threshold", 0.05))

    def __init__(self):
        self.momentum = bt.indicators.Momentum(self.data.close, period=self.params.lookback)

    def next(self):
        if self.momentum[0] > self.params.threshold and not self.position:
            self.buy()
        elif self.momentum[0] < -self.params.threshold and self.position:
            self.sell()
            