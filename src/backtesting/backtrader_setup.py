import backtrader as bt

class MovingAverageStrategy(bt.Strategy):
    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=10)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=50)

    def next(self):
        if self.short_ma > self.long_ma and not self.position:
            self.buy()
        elif self.short_ma < self.long_ma and self.position:
            self.sell()

if __name__ == "__main__":
    cerebro = bt.Cerebro()
    data = bt.feeds.GenericCSVData(
        dataname="data/raw/aapl_historical.csv",
        dtformat="%Y-%m-%d",
        openinterest=-1
    )
    cerebro.adddata(data)
    cerebro.addstrategy(MovingAverageStrategy)
    cerebro.run()
    cerebro.plot()
    