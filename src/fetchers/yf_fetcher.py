import yfinance as yf
from datetime import datetime
from src.utils.database import insert_yahoo_finance_data, insert_options_data

def convert_unix_to_datetime(unix_timestamp):
    """
    Convert a Unix timestamp to a Python datetime object.
    
    Args:
        unix_timestamp (int|str|None): Unix timestamp in seconds.
        
    Returns:
        datetime|None: Converted datetime object or None if the input is invalid.
    """
    try:
        if unix_timestamp is None or str(unix_timestamp).strip() == "":
            return None
        return datetime.utcfromtimestamp(int(unix_timestamp))
    except (ValueError, TypeError):
        print(f"⚠️ Invalid Unix timestamp: {unix_timestamp}")
        return None

def fetch_yahoo_finance_data(symbols):
    """
    Fetch historical and key metrics data from Yahoo Finance and insert into the database.
    """
    data_to_insert = []
    options_data_to_insert = []

    def safe_convert(value, target_type, default=None):
        """Safely convert a value to a specified type, returning default on failure."""
        try:
            if value is None:
                return default
            if isinstance(value, (list, dict)):  # Ensure no complex types are passed
                return default
            return target_type(value)
        except (ValueError, TypeError):
            return default

    def parse_market_cap(market_cap):
        """Parse market cap from yfinance info (if needed)."""
        return safe_convert(market_cap, float)

    for symbol in symbols:
        print(f"📊 Fetching Yahoo Finance data for {symbol}...")
        stock = yf.Ticker(symbol)

        # Fetch historical price data
        try:
            history = stock.history(period="1y", interval="1h")
        except Exception as e:
            print(f"⚠️ Failed to fetch historical data for {symbol}: {e}")
            history = None

        # Fetch additional stock info
        try:
            info = stock.info
        except Exception as e:
            print(f"⚠️ Failed to fetch stock info for {symbol}: {e}")
            info = {}

        # Fetch dividends and splits
        try:
            dividends = stock.dividends
            splits = stock.splits
        except Exception as e:
            print(f"⚠️ Failed to fetch dividends or splits for {symbol}: {e}")
            dividends, splits = None, None

        # Extract fields from yfinance
        target_est = info.get("targetMeanPrice")
        beta = info.get("beta")
        eps = info.get("trailingEps")
        # Extract fields from yfinance, converting Unix timestamps to datetime
        earnings_date = convert_unix_to_datetime(info.get("earningsDate"))
        ex_dividend_date = convert_unix_to_datetime(info.get("exDividendDate"))
        forward_div_yield = info.get("dividendYield")
        pe_ratio = info.get("trailingPE")
        market_cap_numeric = parse_market_cap(info.get("marketCap"))

        # Prepare data for insertion
        if history is not None:
            for date, row in history.iterrows():
                data_to_insert.append((
                    symbol,
                    date,  # Ensure this is a proper datetime object
                    safe_convert(row.get("Open"), float, None),
                    safe_convert(row.get("High"), float, None),
                    safe_convert(row.get("Low"), float, None),
                    safe_convert(row.get("Close"), float, None),
                    safe_convert(row.get("Volume"), int, None),
                    safe_convert(dividends.get(date, None) if dividends is not None else None, float, None),
                    safe_convert(splits.get(date, None) if splits is not None else None, float, None),
                    safe_convert(target_est, float, None),
                    safe_convert(beta, float, None),
                    safe_convert(eps, float, None),
                    safe_convert(earnings_date, datetime, None),  # Ensure this is a proper datetime object
                    safe_convert(ex_dividend_date, datetime, None),  # Ensure this is a proper datetime object
                    safe_convert(forward_div_yield, float, None),
                    safe_convert(pe_ratio, float, None),
                    safe_convert(market_cap_numeric, float, None)
                ))

        # Fetch options data
        try:
            options = stock.options
            for expiration_date in options:
                options_chain = stock.option_chain(expiration_date)
                for option_type, data in zip(["call", "put"], [options_chain.calls, options_chain.puts]):
                    for _, row in data.iterrows():
                        options_data_to_insert.append((
                            symbol,
                            expiration_date,
                            option_type,
                            safe_convert(row.get("strike"), float),
                            safe_convert(row.get("lastPrice"), float),
                            safe_convert(row.get("bid"), float),
                            safe_convert(row.get("ask"), float),
                            safe_convert(row.get("change"), float),
                            safe_convert(row.get("percentChange"), float),
                            safe_convert(row.get("volume"), int),
                            safe_convert(row.get("openInterest"), int),
                            safe_convert(row.get("impliedVolatility"), float)
                        ))
        except Exception as e:
            print(f"⚠️ Failed to fetch options data for {symbol}: {e}")

        # Insert data into the database
        if data_to_insert:
            insert_yahoo_finance_data(data_to_insert)
        else:
            print("⚠️ No data fetched to insert.")

        if options_data_to_insert:
            insert_options_data(options_data_to_insert)
        else:
            print("⚠️ No options data fetched to insert.")

if __name__ == "__main__":
    fetch_yahoo_finance_data(["AAPL", "MSFT", "GOOGL", "AMZN"])
