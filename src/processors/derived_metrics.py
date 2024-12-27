import pandas as pd
import numpy as np
from src.utils.database import fetch_data, insert_derived_metrics
from datetime import timedelta

def calculate_log_returns(df):
    """
    Calculate logarithmic returns.
    """
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    return df

def calculate_moving_averages(df):
    """
    Calculate 50-day and 200-day moving averages.
    """
    df['moving_avg_50'] = df['close'].rolling(window=50).mean()
    df['moving_avg_200'] = df['close'].rolling(window=200).mean()
    return df

def calculate_rsi(df, window=14):
    """
    Calculate Relative Strength Index (RSI).
    """
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def calculate_macd(df):
    """
    Calculate Moving Average Convergence Divergence (MACD).
    """
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    return df

def calculate_pe_ratio(df):
    """
    Placeholder for P/E ratio calculation. You would need earnings data.
    """
    # Assuming earnings are fetched or present in the dataset
    if 'earnings' in df.columns and df['earnings'].sum() > 0:
        df['pe_ratio'] = df['close'] / df['earnings']
    else:
        df['pe_ratio'] = None
    return df

def calculate_market_cap(df):
    """
    Placeholder for Market Cap calculation. You would need outstanding shares.
    """
    # Assuming outstanding shares data is available
    if 'outstanding_shares' in df.columns:
        df['market_cap'] = df['close'] * df['outstanding_shares']
    else:
        df['market_cap'] = None
    return df

def populate_derived_metrics():
    """
    Populate the derived_metrics table based on historical and real-time market data.
    """
    # Fetch historical market data
    query = """
        SELECT symbol, datetime, close, volume
        FROM historical_market_data
        ORDER BY symbol, datetime
    """
    historical_data = fetch_data(query)

    if historical_data.empty:
        print("⚠️ No historical data available for derived metrics calculation.")
        return

    # Perform calculations
    historical_data = calculate_log_returns(historical_data)
    historical_data = calculate_moving_averages(historical_data)
    historical_data = calculate_rsi(historical_data)
    historical_data = calculate_macd(historical_data)
    historical_data = calculate_pe_ratio(historical_data)
    historical_data = calculate_market_cap(historical_data)

    # Select relevant columns for insertion
    derived_data = historical_data[[
        'symbol', 'datetime', 'log_returns', 'pe_ratio', 'market_cap',
        'moving_avg_50', 'moving_avg_200', 'rsi', 'macd'
    ]].dropna()

    # Convert to list of tuples for insertion
    data_to_insert = derived_data.to_records(index=False).tolist()

    # Insert into derived_metrics table
    rows_inserted = insert_derived_metrics(data_to_insert)
    print(f"✅ {rows_inserted} rows inserted into derived_metrics table.")

if __name__ == "__main__":
    populate_derived_metrics()
