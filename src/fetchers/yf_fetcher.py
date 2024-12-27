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
        earnings_date = safe_convert(quote_table.get("Earnings Date"), str)
        ex_dividend_date = safe_convert(quote_table.get("Ex-Dividend Date"), str)
        forward_div_yield = safe_convert(quote_table.get("Forward Dividend & Yield"), str)
        pe_ratio = safe_convert(quote_table.get("PE Ratio (TTM)"), float)
        market_cap_numeric = parse_market_cap(quote_table.get("Market Cap"))

        # Prepare data for insertion
        if history is not None:
            for date, row in history.iterrows():
                data_to_insert.append((
                    symbol,
                    date,
                    safe_convert(row.get('Open'), float, None),
                    safe_convert(row.get('High'), float, None),
                    safe_convert(row.get('Low'), float, None),
                    safe_convert(row.get('Close'), float, None),
                    safe_convert(row.get('Volume'), int, None),
                    safe_convert(dividends.get(date, None), float, None),  # Match dividend dates
                    safe_convert(target_est, float, None),
                    safe_convert(beta, float, None),
                    safe_convert(eps, float, None),
                    safe_convert(earnings_date, str, None),
                    safe_convert(ex_dividend_date, str, None),
                    safe_convert(forward_div_yield, str, None),
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
                            safe_convert(row.get('strike'), float),
                            safe_convert(row.get('lastPrice'), float),
                            safe_convert(row.get('bid'), float),
                            safe_convert(row.get('ask'), float),
                            safe_convert(row.get('change'), float),
                            safe_convert(row.get('percentChange'), float),
                            safe_convert(row.get('volume'), int),
                            safe_convert(row.get('openInterest'), int),
                            safe_convert(row.get('impliedVolatility'), float)
                        ))
        except Exception as e:
            print(f"⚠️ Failed to fetch options data for {symbol}: {e}")

        # Insert data into the database
        if data_to_insert:
            try:
                print(f"🔍 Data to insert into yahoo_finance_data: {data_to_insert[:5]}")  # Print first 5 rows for debugging
                insert_yahoo_finance_data(data_to_insert)
                print(f"✅ Successfully inserted Yahoo Finance data for {len(symbols)} symbols.")
            except Exception as e:
                print(f"❌ Error inserting Yahoo Finance data: {e}")
        else:
            print("⚠️ No data fetched to insert.")

        if options_data_to_insert:
            try:
                print(f"🔍 Options data to insert: {options_data_to_insert[:5]}")  # Print first 5 rows for debugging
                insert_options_data(options_data_to_insert)
                print(f"✅ Successfully inserted options data for {len(symbols)} symbols.")
            except Exception as e:
                print(f"❌ Error inserting options data: {e}")
        else:
            print("⚠️ No options data fetched to insert.")

if __name__ == "__main__":
    fetch_yahoo_finance_data(["AAPL", "MSFT", "GOOGL", "AMZN"])
