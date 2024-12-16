import pandas as pd
from src.utils.database import insert_trade_logs
from src.fetchers.alpaca_fetcher import fetch_historical_data

def moving_average_crossover_strategy(data, short_window=10, long_window=50):
    """
    Simulate a simple moving average crossover strategy.
    
    Args:
        data (pd.DataFrame): Historical stock data with columns ['datetime', 'close'].
        short_window (int): Window size for the short moving average.
        long_window (int): Window size for the long moving average.

    Returns:
        list: List of trades, where each trade is a dict with keys:
            - symbol
            - action (BUY/SELL)
            - quantity
            - price_per_share
            - datetime
            - pnl
    """
    data['SMA_Short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['close'].rolling(window=long_window).mean()
    
    trades = []
    position = 0  # 1 for long, -1 for short, 0 for no position
    quantity = 10  # Fixed quantity for each trade

    for i in range(len(data)):
        if i == 0:
            continue
        row = data.iloc[i]
        prev_row = data.iloc[i - 1]
        
        # Buy Signal: Short MA crosses above Long MA
        if row['SMA_Short'] > row['SMA_Long'] and prev_row['SMA_Short'] <= prev_row['SMA_Long']:
            if position == 0:
                price = row['close']
                trades.append({
                    "symbol": "AAPL",
                    "action": "BUY",
                    "quantity": quantity,
                    "price_per_share": price,
                    "datetime": row['datetime'],
                    "pnl": 0,  # Unrealized PnL
                })
                position = 1

        # Sell Signal: Short MA crosses below Long MA
        elif row['SMA_Short'] < row['SMA_Long'] and prev_row['SMA_Short'] >= prev_row['SMA_Long']:
            if position == 1:
                price = row['close']
                entry_trade = trades[-1]
                pnl = (price - entry_trade['price_per_share']) * quantity
                trades.append({
                    "symbol": "AAPL",
                    "action": "SELL",
                    "quantity": quantity,
                    "price_per_share": price,
                    "datetime": row['datetime'],
                    "pnl": pnl,
                })
                position = 0

    return trades

def log_backtesting_trades(strategy_name, trades):
    """
    Log trades from a backtesting session.

    Args:
        strategy_name (str): Name of the strategy.
        trades (list): List of trades, where each trade is a dict with keys:
            - symbol
            - action (BUY/SELL)
            - quantity
            - price_per_share
            - datetime
            - pnl
    """
    # Convert data to Python-native types
    data = [
        (
            strategy_name,
            trade["symbol"],
            trade["action"],
            trade["quantity"],
            float(trade["price_per_share"]),  # Convert np.float64 to float
            trade["datetime"],
            float(trade["pnl"]),  # Convert np.float64 to float
        )
        for trade in trades
    ]
    try:
        insert_trade_logs(data)
        print(f"Logged {len(trades)} trades into trade_logs.")
    except Exception as e:
        print(f"Error inserting trade logs: {e}")

def backtest():
    """
    Backtest a strategy and print key performance metrics.
    """
    # Example: Fetch historical data for AAPL
    data = fetch_historical_data(["AAPL"], "2020-01-01", "2022-12-31")

    # Debugging: Print the fetched data
    print(f"Fetched data: {data}")

    # Convert to DataFrame if not already in the correct format
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Check if data is empty
    if data.empty:
        print("Error: No data fetched. Ensure fetch_and_store_historical_data is returning valid results.")
        return

    data.columns = ["symbol", "datetime", "open", "high", "low", "close", "volume"]

    # Run the strategy
    trades = moving_average_crossover_strategy(data)

    # Log trades into the database
    log_backtesting_trades("Moving Average Crossover", trades)

    # Calculate performance metrics
    total_pnl = sum(trade['pnl'] for trade in trades if trade['action'] == "SELL")
    win_trades = len([trade for trade in trades if trade['pnl'] > 0])
    total_trades = len([trade for trade in trades if trade['action'] == "SELL"])
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

    print(f"Total PnL: ${total_pnl:.2f}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Trades: {total_trades}")

if __name__ == "__main__":
    backtest()
