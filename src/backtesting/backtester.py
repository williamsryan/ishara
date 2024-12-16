import backtrader as bt
from datetime import datetime
from src.utils.data_loader import load_data_from_db
from src.utils.database import connect_to_db
from src.backtesting.strategies.moving_avg import MovingAverageCrossover
from src.backtesting.strategies.momentum import MomentumStrategy

from sqlalchemy import text

def store_backtest_result(strategy_name, symbol, start_date, end_date, initial_value, final_value):
    """
    Store backtest results in the database.

    Args:
        strategy_name (str): Name of the strategy.
        symbol (str): Stock ticker.
        start_date (str): Start date of the backtest.
        end_date (str): End date of the backtest.
        initial_value (float): Starting portfolio value.
        final_value (float): Ending portfolio value.
    """
    engine = connect_to_db()
    return_percentage = ((final_value - initial_value) / initial_value) * 100

    query = text("""
    INSERT INTO backtest_results (strategy_name, symbol, start_date, end_date, initial_value, final_value, return_percentage)
    VALUES (:strategy_name, :symbol, :start_date, :end_date, :initial_value, :final_value, :return_percentage)
    """)

    params = {
        "strategy_name": strategy_name,
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "initial_value": initial_value,
        "final_value": final_value,
        "return_percentage": return_percentage,
    }

    try:
        with engine.begin() as conn:  # Use `begin()` to auto-commit
            conn.execute(query, params)
            print(f"Results for {strategy_name} on {symbol} stored successfully.")
    except Exception as e:
        print(f"Error storing backtest result: {e}")

def run_backtests(symbols, start_date=None, end_date=None):
    """
    Run multiple backtests for different strategies using data from the database.

    Args:
        symbols (list): List of stock tickers to backtest.
        start_date (str): Start date for backtesting.
        end_date (str): End date for backtesting.
    """
    strategies = {
        "MovingAverageCrossover": MovingAverageCrossover,
        "MomentumStrategy": MomentumStrategy,
    }

    for symbol in symbols:
        print(f"Running backtests for {symbol}...")

        for strategy_name, strategy_class in strategies.items():
            print(f" - Testing strategy: {strategy_name}")

            # Initialize Backtrader engine
            cerebro = bt.Cerebro()
            cerebro.addstrategy(strategy_class)

            # Load data
            data = load_data_from_db(symbol, start_date, end_date)
            data_feed = bt.feeds.PandasData(dataname=data)
            cerebro.adddata(data_feed)

            # Set broker starting cash
            initial_cash = 100000
            cerebro.broker.set_cash(initial_cash)

            # Run backtest
            cerebro.run()

            # Calculate final portfolio value
            final_cash = cerebro.broker.getvalue()

            # Store results in the database
            store_backtest_result(strategy_name, symbol, start_date, end_date, initial_cash, final_cash)

if __name__ == "__main__":
    stock_symbols = ["AAPL", "MSFT", "GOOGL"]
    run_backtests(stock_symbols, start_date="2020-01-01", end_date="2022-12-31")
    