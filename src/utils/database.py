import psycopg2
from psycopg2.extras import execute_batch, RealDictCursor
from contextlib import contextmanager
import pandas as pd
import hashlib
from sqlalchemy import create_engine
from src.utils.config import POSTGRES

# Database Configuration
db_host = POSTGRES["host"]
db_name = POSTGRES["dbname"]
db_user = POSTGRES["user"]
db_password = POSTGRES["password"]

# SQLAlchemy Connection String
SQLALCHEMY_DB_URI = f"postgresql+psycopg2://{POSTGRES['user']}:{POSTGRES['password']}@{POSTGRES['host']}/{POSTGRES['dbname']}"

# Table Names
TABLES = {
    "real_time": "real_time_market_data",
    "historical": "historical_market_data",
    "alternative": "alternative_data",
    "yahoo_finance": "yahoo_finance_data",
    "trade_logs": "trade_logs",
    "backtest_results": "backtest_results",
    "derived_metrics": "derived_metrics",
    "options": "options_data",
    "analysis_results": "analysis_results",
    "scraped_data": "scraped_data",
}

# -------------------- CONTEXT MANAGER --------------------

@contextmanager
def connect_to_db():
    """
    Context manager for database connection.
    """
    conn = None
    try:
        conn = psycopg2.connect(**POSTGRES)
        yield conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
    finally:
        if conn:
            conn.close()

def get_sqlalchemy_engine():
    """
    Returns a SQLAlchemy engine for compatibility with Pandas.
    """
    try:
        engine = create_engine(SQLALCHEMY_DB_URI)
        return engine
    except Exception as e:
        print(f"❌ Error creating SQLAlchemy engine: {e}")
        raise

# -------------------- GENERIC INSERT METHODS --------------------

def insert_data(table_name, data, columns, conflict_target=None, conflict_action="DO NOTHING"):
    """
    Insert data into a specified table with optional conflict handling.

    Args:
        table_name (str): The name of the table.
        data (list): List of tuples containing the data to insert.
        columns (list): List of column names corresponding to the data.
        conflict_target (str | list, optional): Column(s) to apply conflict resolution on.
        conflict_action (str, optional): Action to perform on conflict (default: "DO NOTHING").

    Returns:
        int: Number of rows successfully inserted.
    """
    if not data:
        print("⚠️ No data to insert.")
        return 0

    conflict_clause = ""
    if conflict_target:
        target = f"({', '.join(conflict_target)})" if isinstance(conflict_target, list) else f"({conflict_target})"
        conflict_clause = f"ON CONFLICT {target} {conflict_action}"

    query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        {conflict_clause}
    """
    with connect_to_db() as conn:
        try:
            with conn.cursor() as cursor:
                execute_batch(cursor, query, data)
            conn.commit()
            print(f"✅ Successfully inserted {len(data)} records into {table_name}.")
            return len(data)
        except Exception as e:
            conn.rollback()
            print(f"❌ Error inserting data into {table_name}: {e}")
            return 0

# -------------------- VALIDATION METHODS --------------------

def data_exists(table_name, column, value):
    """
    Check if a specific value exists in a column of a table.

    Args:
        table_name (str): The name of the table.
        column (str): The column to check.
        value: The value to look for.

    Returns:
        bool: True if the value exists, False otherwise.
    """
    query = f"SELECT 1 FROM {table_name} WHERE {column} = %s LIMIT 1"
    with connect_to_db() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (value,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"❌ Error checking data existence in {table_name}: {e}")
            return False

# -------------------- SPECIFIC INSERT METHODS --------------------

def insert_real_time_data(data):
    """
    Insert real-time market data into the database.

    Args:
        data (list): List of tuples [(symbol, datetime, open, high, low, close, volume), ...].
    """
    return insert_data(TABLES["real_time"], data, ["symbol", "datetime", "open", "high", "low", "close", "volume"])

def insert_historical_market_data(data):
    """
    Insert historical market data into the database.

    Args:
        data (list): List of tuples [(symbol, datetime, open, high, low, close, volume), ...].
    """
    return insert_data(TABLES["historical"], data, ["symbol", "datetime", "open", "high", "low", "close", "volume"])

def insert_alternative_data(data):
    """
    Insert alternative data into the database.

    Args:
        data (list): List of tuples [(source, symbol, datetime, metric, value, details), ...].
    """
    return insert_data(TABLES["alternative"], data, ["source", "symbol", "datetime", "metric", "value", "details"])

def insert_yahoo_finance_data(data):
    """
    Insert Yahoo Finance data into the database.

    Args:
        data (list): List of tuples [(symbol, date, open, high, low, close, volume,
                                      dividends, target_est, beta, eps, earnings_date,
                                      ex_dividend_date, forward_div_yield, pe_ratio, market_cap), ...].
    """
    table_name = TABLES["yahoo_finance"]
    columns = [
        "symbol",
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "dividends",
        "splits",
        "target_est",
        "beta",
        "eps",
        "earnings_date",
        "ex_dividend_date",
        "forward_div_yield",
        "pe_ratio",
        "market_cap",
    ]

    return insert_data(table_name, data, columns)

def insert_trade_logs(data):
    """
    Insert trade logs into the database.

    Args:
        data (list): List of dictionaries containing trade log entries. Each dictionary should contain:
            - strategy (str): The name of the strategy.
            - symbol (str): The stock ticker symbol.
            - action (str): The trade action ('BUY' or 'SELL').
            - quantity (int): The number of shares traded.
            - price (float): The price per share.
            - datetime (datetime): The date and time of the trade.
            - pnl (float): The profit or loss from the trade.
    """
    table_name = TABLES["trade_logs"]
    columns = ["strategy", "symbol", "action", "quantity", "price", "datetime", "pnl"]

    # Ensure data is in the correct format
    formatted_data = [
        (
            trade["strategy"],
            trade["symbol"],
            trade["action"],
            trade["quantity"],
            trade["price"],
            trade["datetime"],
            trade.get("pnl", None),  # Default to None if 'pnl' is not provided
        )
        for trade in data
    ]

    # Insert formatted data
    return insert_data(table_name, formatted_data, columns)

def insert_options_data(data):
    """
    Insert options data into the database.

    Args:
        data (list of tuples): Options data to insert. Each tuple should contain:
            - symbol (str)
            - expiration_date (date)
            - option_type (str): 'call' or 'put'
            - strike (float)
            - last_price (float)
            - bid (float)
            - ask (float)
            - change (float)
            - percent_change (float)
            - volume (int)
            - open_interest (int)
            - implied_volatility (float)
    """
    table_name = TABLES["options"]
    columns = [
        "symbol",
        "expiration_date",
        "option_type",
        "strike",
        "last_price",
        "bid",
        "ask",
        "change",
        "percent_change",
        "volume",
        "open_interest",
        "implied_volatility"
    ]

    return insert_data(table_name, data, columns)

def insert_derived_metrics(data):
    """
    Insert derived metrics into the database.

    Args:
        data (list): List of tuples [(symbol, datetime, log_returns, pe_ratio, market_cap,
                                      moving_avg_50, moving_avg_200, rsi, macd), ...].
    """
    table_name = TABLES["derived_metrics"]
    columns = [
        "symbol",
        "datetime",
        "log_returns",
        "pe_ratio",
        "market_cap",
        "moving_avg_50",
        "moving_avg_200",
        "rsi",
        "macd"
    ]

    # Delegate to the generic insert_data function
    return insert_data(table_name, data, columns)

def insert_clustering_results(data):
    """
    Insert clustering results into the analysis_results table.

    Args:
        data (list of tuples): List of tuples (symbol, analysis_type, cluster_id, result).
    """
    table_name = TABLES["analysis_results"]
    columns = ["symbol", "analysis_type", "cluster_id", "result"]

    # Add conflict handling for unique analysis ID
    formatted_data = [
        (
            symbol,
            analysis_type,
            cluster_id,
            result,
            generate_analysis_id(symbol, analysis_type, cluster_id, result),
        )
        for symbol, analysis_type, cluster_id, result in data
    ]

    return insert_data(table_name, formatted_data, columns + ["analysis_id"], conflict_target="analysis_id")

def insert_backtest_results(data):
    """
    Insert backtest results into the database.

    Args:
        data (list): List of dictionaries containing backtest results. Each dictionary should contain:
            - strategy (str): Name of the strategy.
            - symbol (str): Stock ticker symbol.
            - start_date (str): Start date of the backtest.
            - end_date (str): End date of the backtest.
            - initial_value (float): Starting value of the portfolio.
            - final_value (float): Final value of the portfolio.
            - return_percentage (float): Portfolio return percentage.

    Returns:
        int: Number of rows successfully inserted.
    """
    table_name = TABLES["backtest_results"]
    columns = [
        "strategy_name",
        "symbol",
        "start_date",
        "end_date",
        "initial_value",
        "final_value",
        "return_percentage",
    ]

    # Convert list of dictionaries into list of tuples
    formatted_data = [
        (
            result["strategy"],
            result["symbol"],
            result["start_date"],
            result["end_date"],
            result["initial_value"],
            result["final_value"],
            result["return_percentage"],
        )
        for result in data
    ]

    # Insert data using the generic insert_data method
    return insert_data(table_name, formatted_data, columns)

def insert_symbols(data):
    """
    Insert symbol data into the symbols table.

    Args:
        data (list of tuples): List of tuples containing symbol data. Each tuple should contain:
            - symbol (str): Stock ticker symbol
            - name (str): Full company name
            - sector (str): Sector or industry
            - exchange (str): Stock exchange

    Returns:
        int: Number of rows successfully inserted.
    """
    table_name = "symbols"
    columns = ["symbol", "name", "sector", "exchange"]

    return insert_data(table_name, data, columns)

def insert_scraped_data(data):
    """
    Insert financial data into the scraped_data table.

    Args:
        data (list of tuples): List of tuples containing financial data. Each tuple should contain:
            - source (str): Source of the data.
            - symbol (str): Stock ticker symbol (optional).
            - headline (str): Headline of the article or report.
            - summary (str): Summary of the content (optional).
            - sentiment (str): Sentiment label (e.g., 'positive', 'neutral', 'negative').
            - publish_date (datetime): Publish date of the content.

    Returns:
        int: Number of rows successfully inserted.
    """
    table_name = "scraped_data"
    columns = ["source", "symbol", "headline", "summary", "sentiment", "publish_date"]

    # Ensure data is in the correct format
    formatted_data = [
        (
            record.get("source"),
            record.get("symbol"),
            record.get("headline"),
            record.get("summary"),
            record.get("sentiment"),
            record.get("publish_date"),
        )
        for record in data
    ]

    # Use the generic insert_data function
    return insert_data(table_name, formatted_data, columns)

# -------------------- FETCH METHODS --------------------

def fetch_data(query, params=None):
    """
    Execute a query and fetch results as a Pandas DataFrame.

    Args:
        query (str): SQL query to execute.
        params (tuple, optional): Query parameters.

    Returns:
        pd.DataFrame: Query results as a Pandas DataFrame.
    """
    engine = get_sqlalchemy_engine()
    try:
        # print(f"DEBUG: Query to execute:\n{query}")
        results = pd.read_sql_query(query, con=engine, params=params)
        # print(f"DEBUG: Query results:\n{results.head()}")
        return results
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()
    
def fetch_as_dataframe(query, params=None):
    """
    Fetch data from the database and return it as a Pandas DataFrame.
    
    Args:
        query (str): SQL query to execute.
        params (tuple): Parameters for the query.
    
    Returns:
        pd.DataFrame: DataFrame containing query results.
    """
    engine = get_sqlalchemy_engine() 
    try:
        # Execute the query and fetch results as a DataFrame
        df = pd.read_sql_query(query, con=engine, params=params)
        return df
    except Exception as e:
        print(f"❌ Error fetching data as DataFrame: {e}")
        return pd.DataFrame()

# -------------------- UTILITIES --------------------

def execute_query(query, params=None, fetch=False):
    """
    Execute a query against the database.
    
    Args:
        query (str): SQL query to execute.
        params (tuple): Parameters for the query.
        fetch (bool): Whether to fetch data (True) or commit changes (False).
    
    Returns:
        list | None: Fetched results or None if no fetch is requested.
    """
    with connect_to_db() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            conn.rollback()
    return None

def delete_duplicates(table_name, unique_columns):
    """
    Remove duplicate rows from a table based on unique columns.

    Args:
        table_name (str): The name of the table.
        unique_columns (list): List of columns that define uniqueness.
    """
    query = f"""
        DELETE FROM {table_name} a
        USING {table_name} b
        WHERE a.ctid < b.ctid
        AND { ' AND '.join([f'a.{col} = b.{col}' for col in unique_columns]) }
    """
    with connect_to_db() as conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()
            print(f"✅ Removed duplicate rows from {table_name}.")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error removing duplicates from {table_name}: {e}")

def generate_analysis_id(symbol, analysis_type, cluster_id, result):
    """
    Generate a unique hash for an analysis result.
    """
    hash_input = f"{symbol}-{analysis_type}-{cluster_id}-{result}"
    return hashlib.md5(hash_input.encode()).hexdigest()
