import backtrader as bt
import pandas as pd
from datetime import datetime
from src.fetchers.alpaca_fetcher import fetch_historical_data
from src.utils.database import insert_trade_logs

class MovingAverageCrossover(bt.Strategy):
    """
    Backtrader strategy for moving average crossover.
    """
    params = (
        ("short_window", 10),  # Short moving average period
        ("long_window", 50),  # Long moving average period
        ("quantity", 10),     # Number of shares to trade
    )

    def __init__(self):
        # Initialize short and long moving averages
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_window
        )
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_window
        )

        self.orders = []  # To track completed orders

    def next(self):
        # Check for crossover signals
        if self.sma_short > self.sma_long and not self.position:
            self.buy(size=self.params.quantity)
        elif self.sma_short < self.sma_long and self.position:
            self.sell(size=self.params.quantity)

    def notify_order(self, order):
        """
        Track the lifecycle of orders and record completed ones.
        """
        if order.status == order.Completed:
            self.orders.append({
                "symbol": self.data._name,
                "action": "BUY" if order.isbuy() else "SELL",
                "quantity": order.executed.size,
                "price_per_share": order.executed.price,
                "datetime": bt.num2date(order.executed.dt),  # Convert to datetime
                "pnl": order.executed.pnl
            })

def fetch_data_to_backtrader(symbol, start_date, end_date):
    """
    Fetch historical data using Alpaca and format for Backtrader.

    Args:
        symbol (str): Stock symbol.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).

    Returns:
        bt.feeds.PandasData: Backtrader-compatible data feed with symbol attached.
    """
    data = fetch_historical_data([symbol], start_date, end_date)
    data["datetime"] = pd.to_datetime(data["datetime"])
    data.set_index("datetime", inplace=True)
    data_feed = bt.feeds.PandasData(
        dataname=data,
        datetime=None,
        open="open",
        high="high",
        low="low",
        close="close",
        volume="volume",
        name=symbol  # Attach the symbol here
    )
    return data_feed

def log_backtesting_results(cerebro, strategy_name):
    """
    Log trades and performance metrics after backtesting.

    Args:
        cerebro (bt.Cerebro): Backtrader engine after backtesting.
        strategy_name (str): Name of the strategy.
    """
    trades = []
    for strat in cerebro.runstrats:
        for order in strat[0].orders:  # Access orders logged in the strategy
            trades.append((
                strategy_name,
                order["symbol"],
                order["action"],
                order["quantity"],
                order["price_per_share"],
                order["datetime"],
                order["pnl"],
            ))

    # Insert trades into the database
    if trades:
        try:
            insert_trade_logs(trades)
            print(f"Logged {len(trades)} trades into trade_logs.")
        except Exception as e:
            print(f"Error inserting trade logs: {e}")
    else:
        print("No trades to log.")

    # Performance Metrics
    final_value = cerebro.broker.getvalue()
    starting_cash = cerebro.broker.startingcash
    pnl = final_value - starting_cash
    print(f"Final Portfolio Value: ${final_value:.2f}")
    print(f"Total PnL: ${pnl:.2f}")

def backtest():
    """
    Run a Backtrader backtest for a moving average crossover strategy.
    """
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(100000)  # Initial cash
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission

    # Fetch data for AAPL
    data_feed = fetch_data_to_backtrader("AAPL", "2020-01-01", "2022-12-31")
    cerebro.adddata(data_feed)

    # Add strategy
    cerebro.addstrategy(MovingAverageCrossover)

    # Run backtest
    cerebro.run()

    # Log results
    log_backtesting_results(cerebro, "Moving Average Crossover")

    # Show the portfolio's final value and plot the results
    cerebro.plot()


if __name__ == "__main__":
    backtest()
