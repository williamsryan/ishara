import psycopg2
import pandas as pd
from src.utils.config import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

def connect_to_db():
    return psycopg2.connect(
        dbname=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD
    )

def insert_stock_data(data, symbol):
    """Insert historical stock data into the database."""
    conn = connect_to_db()
    cursor = conn.cursor()
    for _, row in data.iterrows():
        cursor.execute("""
            INSERT INTO stock_data (symbol, datetime, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (symbol, row["timestamp"], row["open"], row["high"], row["low"], row["close"], row["volume"]))
    conn.commit()
    conn.close()
    