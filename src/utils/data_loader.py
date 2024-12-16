import pandas as pd
from src.utils.database import connect_to_db

def load_data_from_db(symbol, start_date=None, end_date=None):
    """
    Load historical data for a given symbol from PostgreSQL using SQLAlchemy.

    Args:
        symbol (str): Stock ticker (e.g., "AAPL").
        start_date (str): Optional start date (YYYY-MM-DD).
        end_date (str): Optional end date (YYYY-MM-DD).

    Returns:
        pd.DataFrame: DataFrame of historical stock data.
    """
    engine = connect_to_db()
    query = """
    SELECT 
        datetime, open, high, low, close, volume 
    FROM stock_data 
    WHERE symbol = %(symbol)s
    """
    params = {"symbol": symbol}

    if start_date:
        query += " AND datetime >= %(start_date)s"
        params["start_date"] = start_date
    if end_date:
        query += " AND datetime <= %(end_date)s"
        params["end_date"] = end_date

    # Execute the query and return the DataFrame
    df = pd.read_sql_query(query, engine, params=params)

    # Ensure datetime column is in datetime64 format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Set index for Backtrader
    df.set_index('datetime', inplace=True)
    return df
