import backtrader as bt
import pandas as pd
from src.utils.database import fetch_data, insert_backtest_results
from src.backtesting.strategies.moving_avg import MovingAverageCrossover
from src.backtesting.strategies.momentum import MomentumStrategy
import plotly.graph_objects as go

def load_data_from_db(symbol, start_date, end_date):
    """
    Fetch stock data using fetch_data for Backtrader.

    Args:
        symbol (str): Stock ticker.
        start_date (str): Start date of data.
        end_date (str): End date of data.

    Returns:
        pd.DataFrame: Stock data formatted for Backtrader.
    """
    query = """
    SELECT datetime, open, high, low, close, volume
    FROM historical_market_data
    WHERE symbol = %s AND datetime BETWEEN %s AND %s
    ORDER BY datetime ASC
    """
    params = (symbol, start_date, end_date)
    data = fetch_data(query, params)

    if data.empty:
        raise ValueError(f"No data found for {symbol} between {start_date} and {end_date}.")

    data["datetime"] = pd.to_datetime(data["datetime"])
    data.set_index("datetime", inplace=True)
    return data

def store_backtest_result(strategy_name, portfolio_results, start_date, end_date):
    """
    Store aggregated backtest results in the database.

    Args:
        strategy_name (str): Strategy name.
        portfolio_results (dict): Results with symbols and their final values.
        start_date (str): Start date of backtest.
        end_date (str): End date of backtest.
    """
    records = []
    for symbol, result in portfolio_results.items():
        initial_value = result["initial_value"]
        final_value = result["final_value"]
        return_percentage = ((final_value - initial_value) / initial_value) * 100
        records.append((
            strategy_name,
            symbol,
            start_date,
            end_date,
            initial_value,
            final_value,
            return_percentage
        ))

    # Use the new insert method
    inserted_count = insert_backtest_results(records)
    print(f"✅ Stored {inserted_count} backtest results for strategy '{strategy_name}'")

def run_portfolio_backtest(portfolio, start_date, end_date, strategy_name):
    """
    Run backtest for a portfolio of stocks.

    Args:
        portfolio (dict): Portfolio stocks and weights.
        start_date (str): Start date.
        end_date (str): End date.
        strategy_name (str): Strategy to apply.

    Returns:
        dict: Portfolio results and equity curves.
    """
    strategies = {
        "MovingAverageCrossover": MovingAverageCrossover,
        "MomentumStrategy": MomentumStrategy,
    }

    if strategy_name not in strategies:
        raise ValueError(f"Invalid strategy: {strategy_name}")

    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategies[strategy_name])

    portfolio_results = {}
    for symbol, weight in portfolio.items():
        print(f"Adding {symbol} to portfolio with weight {weight}...")
        data = load_data_from_db(symbol, start_date, end_date)
        data_feed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(data_feed, name=symbol)

    cerebro.broker.set_cash(100000)
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    for symbol, weight in portfolio.items():
        portfolio_results[symbol] = {
            "initial_value": 100000 * weight,
            "final_value": final_value,
        }

    return portfolio_results

def run_backtests(symbols, start_date, end_date, strategy_name):
    """
    Run backtests for the specified symbols and strategy.

    Args:
        symbols (list): List of stock tickers.
        start_date (str): Start date.
        end_date (str): End date.
        strategy_name (str): Strategy to apply.

    Returns:
        None
    """
    strategies = {
        "MovingAverageCrossover": MovingAverageCrossover,
        "MomentumStrategy": MomentumStrategy,
    }

    if strategy_name not in strategies:
        raise ValueError(f"Invalid strategy: {strategy_name}")

    portfolio = {symbol: 1 / len(symbols) for symbol in symbols}
    results = run_portfolio_backtest(portfolio, start_date, end_date, strategy_name=strategy_name)
    store_backtest_result(strategy_name, results, start_date, end_date)
