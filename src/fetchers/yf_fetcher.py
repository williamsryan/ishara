import yfinance as yf
from datetime import datetime
from src.lib.stock_info import get_quote_table
from src.utils.database import insert_yahoo_finance_data, insert_options_data

def fetch_yahoo_finance_data(symbols):
    """
    Fetch historical and key metrics data from Yahoo Finance and insert into the database.
    """
    data_to_insert = []
    options_data_to_insert = []

    def safe_convert(value, target_type):
        """Safely convert a value to a specified type, returning None on failure."""
        try:
            return target_type(value)
        except (ValueError, TypeError):
            return None

    def parse_market_cap(market_cap_str):
        """Parse market cap string into numeric value."""
        if isinstance(market_cap_str, str):
            multiplier = {"T": 1e12, "B": 1e9, "M": 1e6}
            try:
                return float(market_cap_str[:-1]) * multiplier.get(market_cap_str[-1], 1)
            except (ValueError, KeyError):
                pass
        return None

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
            dividends = stock.dividends
        except Exception as e:
            print(f"⚠️ Failed to fetch stock info or dividends for {symbol}: {e}")
            info, dividends = {}, {}

        # Fetch quote table
        try:
            quote_table = get_quote_table(symbol, dict_result=True)
        except Exception as e:
            print(f"⚠️ Failed to fetch quote table for {symbol}: {e}")
            quote_table = {}

        # Extract fields from the quote table
        target_est = safe_convert(quote_table.get("1y Target Est"), float)
        beta = safe_convert(quote_table.get("Beta (5Y Monthly)"), float)
        eps = safe_convert(quote_table.get("EPS (TTM)"), float)
        earnings_date = quote_table.get("Earnings Date")
        ex_dividend_date = quote_table.get("Ex-Dividend Date")
        forward_div_yield = quote_table.get("Forward Dividend & Yield")
        pe_ratio = safe_convert(quote_table.get("PE Ratio (TTM)"), float)
        market_cap_numeric = parse_market_cap(quote_table.get("Market Cap"))

        # Prepare data for insertion
        if history is not None:
            for date, row in history.iterrows():
                data_to_insert.append((
                    symbol,
                    date,
                    safe_convert(row['Open'], float),
                    safe_convert(row['High'], float),
                    safe_convert(row['Low'], float),
                    safe_convert(row['Close'], float),
                    safe_convert(row['Volume'], int),
                    dividends.get(date, None),  # Match dividend dates
                    target_est,
                    beta,
                    eps,
                    earnings_date,
                    ex_dividend_date,
                    forward_div_yield,
                    pe_ratio,
                    market_cap_numeric
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
                            safe_convert(row['strike'], float),
                            safe_convert(row['lastPrice'], float),
                            safe_convert(row['bid'], float),
                            safe_convert(row['ask'], float),
                            safe_convert(row['change'], float),
                            safe_convert(row['percentChange'], float),
                            safe_convert(row['volume'], int),
                            safe_convert(row['openInterest'], int),
                            safe_convert(row['impliedVolatility'], float)
                        ))
        except Exception as e:
            print(f"⚠️ Failed to fetch options data for {symbol}: {e}")

    # Insert data into the database
    if data_to_insert:
        insert_yahoo_finance_data(data_to_insert)
        print(f"✅ Successfully inserted Yahoo Finance data for {len(symbols)} symbols.")
    else:
        print("⚠️ No data fetched to insert.")

    if options_data_to_insert:
        insert_options_data(options_data_to_insert)
        print(f"✅ Successfully inserted options data for {len(symbols)} symbols.")
    else:
        print("⚠️ No options data fetched to insert.")

if __name__ == "__main__":
    fetch_yahoo_finance_data(["AAPL", "MSFT", "GOOGL", "AMZN"])
    