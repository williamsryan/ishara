import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd
from src.utils.config import DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

# Global Database Connection Configuration
DB_CONFIG = {
    "host": DATABASE_HOST,
    "dbname": DATABASE_NAME,
    "user": DATABASE_USER,
    "password": DATABASE_PASSWORD
}

def connect_to_db():
    """
    Creates a connection to the database.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

# -------------------- INSERT METHODS --------------------

def insert_historical_market_data(data):
    """
    Insert rows into the historical_market_data table.

    Args:
        data (list): List of tuples [(symbol, datetime, open, high, low, close, volume), ...].
    """
    query = """
        INSERT INTO historical_market_data (symbol, datetime, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    conn = connect_to_db()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            execute_batch(cursor, query, data)
        conn.commit()
        print("✅ Stock data inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting stock data: {e}")
    finally:
        conn.close()

def insert_alternative_data(data):
    """
    Insert rows into the alternative_data table.

    Args:
        data (list): List of tuples [(data_source, symbol, date, key_metric, value), ...].
    """
    query = """
        INSERT INTO alternative_data (data_source, symbol, date, key_metric, value)
        VALUES (%s, %s, %s, %s, %s)
    """
    conn = connect_to_db()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            execute_batch(cursor, query, data)
        conn.commit()
        print("✅ Alternative data inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting alternative data: {e}")
    finally:
        conn.close()

def insert_trade_logs(data):
    """
    Insert rows into the trade_logs table.

    Args:
        data (list): List of tuples [(strategy_name, symbol, action, quantity, price_per_share, datetime, pnl), ...].
    """
    query = """
        INSERT INTO trade_logs (strategy_name, symbol, action, quantity, price_per_share, datetime, pnl)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    conn = connect_to_db()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            execute_batch(cursor, query, data)
        conn.commit()
        print("✅ Trade logs inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting trade logs: {e}")
    finally:
        conn.close()

def insert_backtest_results(results_file):
    """
    Insert backtest results into the backtest_results table.

    Args:
        results_file (str): JSON file containing backtest results.
    """
    query = """
        INSERT INTO backtest_results (symbol, strategy_name, datetime, pnl, trades_count)
        VALUES (%s, %s, %s, %s, %s)
    """
    conn = connect_to_db()
    if not conn:
        return

    try:
        results = pd.read_json(results_file)
        data = [
            (row['symbol'], row['strategy_name'], row['datetime'], row['pnl'], row['trades_count'])
            for _, row in results.iterrows()
        ]
        with conn.cursor() as cursor:
            execute_batch(cursor, query, data)
        conn.commit()
        print("✅ Backtest results inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting backtest results: {e}")
    finally:
        conn.close()

# -------------------- UTILITY METHODS --------------------

def fetch_data(query, params=None):
    """
    Fetch data from the database using a raw SQL query.

    Args:
        query (str): The SQL query to execute.
        params (tuple): Parameters to substitute in the query.

    Returns:
        list: Query results as a list of tuples.
    """
    conn = connect_to_db()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return []
    finally:
        conn.close()
