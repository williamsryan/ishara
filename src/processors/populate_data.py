import pandas as pd
from datetime import datetime
from src.utils.database import connect_to_db
from src.fetchers.alpaca_historical import fetch_historical_data
from src.fetchers.alpaca_realtime import fetch_realtime_data
from src.processors.derived_metrics import calculate_log_returns, calculate_greeks

def populate_historical_data(symbols, start_date, end_date):
    """
    Populate the historical data table with raw and derived metrics.
    """
    conn = connect_to_db()
    for symbol in symbols:
        print(f"Fetching historical data for {symbol}...")
        data = fetch_historical_data(symbol, start_date, end_date, "1Day")
        
        for _, row in data.iterrows():
            log_returns = calculate_log_returns(row["open"], row["close"])
            # Insert into database
            conn.execute("""
                INSERT INTO historical_market_data (symbol, datetime, open, high, low, close, volume, log_returns)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, datetime) DO UPDATE
                SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
                    close = EXCLUDED.close, volume = EXCLUDED.volume, log_returns = EXCLUDED.log_returns
            """, (symbol, row["datetime"], row["open"], row["high"], row["low"], row["close"], row["volume"], log_returns))
        print(f"✅ Historical data for {symbol} populated.")
    conn.commit()
    conn.close()

def populate_realtime_data(symbols):
    """
    Populate the real-time data table with raw and derived metrics.
    """
    conn = connect_to_db()
    data = fetch_realtime_data(symbols)
    for symbol, row in data.iterrows():
        log_returns = calculate_log_returns(row["open"], row["close"])
        # Insert into database
        conn.execute("""
            INSERT INTO real_time_market_data (symbol, datetime, open, high, low, close, volume, log_returns)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, datetime) DO UPDATE
            SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
                close = EXCLUDED.close, volume = EXCLUDED.volume, log_returns = EXCLUDED.log_returns
        """, (symbol, row["datetime"], row["open"], row["high"], row["low"], row["close"], row["volume"], log_returns))
    conn.commit()
    conn.close()
    print("✅ Real-time data populated.")

def populate_company_analysis():
    """
    Populate the company_analysis table with Greeks and derived metrics for options.
    """
    conn = connect_to_db()
    query = """
    SELECT symbol, close AS spot_price, pe_ratio, market_cap
    FROM historical_market_data
    WHERE close IS NOT NULL
    """
    data = pd.read_sql_query(query, conn)

    for _, row in data.iterrows():
        # Greeks Calculation (replace placeholder values with real inputs)
        delta, gamma, theta, vega = calculate_greeks(
            spot=row["spot_price"],
            strike=100,    # Replace with actual strike price
            time=0.5,      # Replace with time to maturity in years
            rate=0.01,     # Risk-free interest rate
            volatility=0.2 # Implied volatility
        )

        conn.execute("""
            INSERT INTO company_analysis (symbol, datetime, delta, gamma, theta, vega, pe_ratio, market_cap)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, datetime) DO UPDATE
            SET delta = EXCLUDED.delta, gamma = EXCLUDED.gamma, theta = EXCLUDED.theta, 
                vega = EXCLUDED.vega, pe_ratio = EXCLUDED.pe_ratio, market_cap = EXCLUDED.market_cap
        """, (row["symbol"], datetime.now(), delta, gamma, theta, vega, row["pe_ratio"], row["market_cap"]))
    conn.commit()
    conn.close()
    print("✅ Company analysis populated.")
    