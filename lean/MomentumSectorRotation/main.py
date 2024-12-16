# region imports
from AlgorithmImports import *
# endregion

class MomentumSectorRotation(QCAlgorithm):

    def initialize(self):
        # Locally Lean installs free sample data, to download more data please visit https://www.quantconnect.com/docs/v2/lean-cli/datasets/downloading-data
        self.set_start_date(2013, 10, 7)  # Set Start Date
        self.set_end_date(2013, 10, 11)  # Set End Date
        self.set_cash(100000)  # Set Strategy Cash

        # Define sectors using ETFs
        self.sector_etfs = {
            "Technology": self.AddEquity("XLK", Resolution.MINUTE).Symbol,
            "Financials": self.AddEquity("XLF", Resolution.MINUTE).Symbol,
            "Healthcare": self.AddEquity("XLV", Resolution.MINUTE).Symbol,
        }

        # Track sector momentum
        self.momentum_scores = {}

        # Rebalance every month
        self.rebalance_schedule = self.Schedule.On(
            self.DateRules.MonthStart(),
            self.TimeRules.At(10, 0),
            self.Rebalance
        )


    def on_data(self, data: Slice):
        """on_data event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        """
        # Calculate momentum scores for sectors
        for sector, symbol in self.sector_etfs.items():
            history = self.History(symbol, 90, Resolution.Daily)["close"]
            if len(history) > 0:
                momentum = (history.iloc[-1] - history.iloc[0]) / history.iloc[0]
                self.momentum_scores[sector] = momentum
        # if not self.portfolio.invested:
        #     self.set_holdings("SPY", 1)
        #     self.debug("Purchased Stock")

    def rebalance(self):
        if len(self.momentum_scores) == 0:
            return

        # Rank sectors by momentum
        ranked_sectors = sorted(self.momentum_scores.items(), key=lambda x: x[1], reverse=True)

        # Focus on top 2 sectors
        top_sectors = [sector for sector, _ in ranked_sectors[:2]]

        # Select stocks within top-performing sectors (mocked with fixed tickers for simplicity)
        stock_allocations = {
            "Technology": ["AAPL", "MSFT"],
            "Financials": ["JPM", "BAC"],
        }

        # Liquidate current holdings
        self.Liquidate()

        # Allocate evenly among selected stocks
        allocation_per_stock = 1.0 / len(top_sectors) / len(stock_allocations[top_sectors[0]])
        for sector in top_sectors:
            for stock in stock_allocations[sector]:
                symbol = self.AddEquity(stock, Resolution.Daily).Symbol
                self.SetHoldings(symbol, allocation_per_stock)

    def on_end_of_algorithm(self):
        stats = self.Statistics
        self.Debug(f"Total Return: {stats['Total Return']}")
        self.Debug(f"Sharpe Ratio: {stats['Sharpe Ratio']}")
        self.Debug(f"Max Drawdown: {stats['Drawdown']}")
