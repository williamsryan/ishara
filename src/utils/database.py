import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from src.utils.config import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host="localhost",
        port=5432
    )

def insert_stock_data(data):
    """
    Insert rows into the stock_data table.

    Args:
        data (list): List of tuples [(symbol, datetime, open, high, low, close, volume), ...].
    """
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO stock_data (symbol, datetime, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        conn.commit()
        print(f"{len(data)} rows inserted into stock_data.")
    except Exception as e:
        print(f"Error inserting stock data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def insert_alternative_data(data):
    """
    Insert rows into the alternative_data table.

    Args:
        data (list): List of tuples [(data_source, symbol, date, key_metric, value), ...].
    """
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO alternative_data (data_source, symbol, date, key_metric, value)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        conn.commit()
        print(f"{len(data)} rows inserted into alternative_data.")
    except Exception as e:
        print(f"Error inserting alternative data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def insert_trade_logs(data):
    """
    Insert rows into the trade_logs table.

    Args:
        data (list): List of tuples [(strategy_name, symbol, action, quantity, price_per_share, datetime, pnl), ...].
    """
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO trade_logs (strategy_name, symbol, action, quantity, price_per_share, datetime, pnl)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        conn.commit()
        print(f"{len(data)} rows inserted into trade_logs.")
    except Exception as e:
        print(f"Error inserting trade logs: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        
def insert_backtest_results(db_connection_string, results_file):
    """
    Insert backtest results into the database.

    Args:
        db_connection_string (str): SQLAlchemy connection string.
        results_file (str): JSON file with backtest results.
    """
    # Load results
    results = pd.read_json(results_file)

    # Connect to the database
    engine = create_engine(db_connection_string)

    # Insert into the backtest_results table
    results.to_sql("backtest_results", engine, if_exists="append", index=False)
    print("Backtest results inserted successfully!")