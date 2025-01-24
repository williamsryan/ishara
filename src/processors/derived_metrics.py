import pandas as pd
import numpy as np
from src.utils.database import fetch_data, insert_derived_metrics
from datetime import timedelta
import talib

def calculate_log_returns(df):
    """Calculate logarithmic returns."""
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    return df

def calculate_technical_indicators(df):
    """Calculate technical indicators using TA-Lib."""
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
    df['sma_200'] = talib.SMA(df['close'], timeperiod=200)
    return df

def populate_derived_metrics():
    """
    Populate the derived_metrics table based on historical and real-time market data.
    """
    # Fetch historical market data
    query = """
        SELECT symbol, datetime, close, volume, open, high, low
        FROM historical_market_data
        ORDER BY symbol, datetime
    """
    historical_data = fetch_data(query)

    if historical_data.empty:
        print("⚠️ No historical data available for derived metrics calculation.")
        return

    # Perform calculations
    historical_data = calculate_log_returns(historical_data)
    historical_data = calculate_technical_indicators(historical_data)

    # Select relevant columns for insertion
    derived_data = historical_data[[
        'symbol', 'datetime', 'log_returns', 'rsi', 'macd', 'macd_signal',
        'macd_hist', 'sma_50', 'sma_200'
    ]].dropna()

    # Convert to list of tuples for insertion
    data_to_insert = derived_data.to_records(index=False).tolist()

    # Insert into derived_metrics table
    rows_inserted = insert_derived_metrics(data_to_insert)
    print(f"✅ {rows_inserted} rows inserted into derived_metrics table.")

if __name__ == "__main__":
    populate_derived_metrics()
    