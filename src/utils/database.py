from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from src.utils.config import DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL, echo=False)  # echo=True for debug logs
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
metadata = MetaData()

def connect_to_db():
    """
    Returns a new session for interacting with the database.
    """
    try:
        session = SessionLocal()
        return session
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
    
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
