from zipline.api import order, record, symbol
from zipline import run_algorithm
import pandas as pd
from datetime import datetime

def initialize(context):
    """Set up the strategy."""
    context.asset = symbol('AAPL')
    context.short_window = 50
    context.long_window = 200

def handle_data(context, data):
    """Define the trading logic."""
    short_mavg = data.history(context.asset, 'price', context.short_window, '1d').mean()
    long_mavg = data.history(context.asset, 'price', context.long_window, '1d').mean()

    if short_mavg > long_mavg:
        order(context.asset, 10)
    elif short_mavg < long_mavg:
        order(context.asset, -10)

    record(short_mavg=short_mavg, long_mavg=long_mavg)

def run_backtest(start_date, end_date, capital):
    """Run the backtest."""
    run_algorithm(
        start=start_date,
        end=end_date,
        capital_base=capital,
        data_frequency='daily',
        initialize=initialize,
        handle_data=handle_data,
        bundle='quantopian-quandl',
    )

if __name__ == "__main__":
    start = datetime(2020, 1, 1)
    end = datetime(2023, 1, 1)
    run_backtest(start_date=start, end_date=end, capital=100000)
    