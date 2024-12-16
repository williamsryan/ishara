import yfinance as yf
from src.utils.database import insert_alternative_data

def fetch_yahoo_key_stats(symbols):
    """
    Fetch key statistics from Yahoo Finance.

    Args:
        symbols (list): List of stock symbols to fetch data for.

    Returns:
        list: List of tuples [(data_source, symbol, date, key_metric, value), ...].
    """
    data = []
    for symbol in symbols:
        print(f"Fetching key statistics for {symbol}...")
        ticker = yf.Ticker(symbol)
        stats = ticker.info

        # Extract relevant metrics
        metrics = {
            "MarketCap": stats.get("marketCap"),
            "PE_Ratio": stats.get("trailingPE"),
            "DividendYield": stats.get("dividendYield"),
            "52_Week_High": stats.get("fiftyTwoWeekHigh"),
            "52_Week_Low": stats.get("fiftyTwoWeekLow")
        }

        for key, value in metrics.items():
            if value is not None:  # Avoid null entries
                data.append(("YahooFinance", symbol, stats.get("regularMarketTime"), key, value))

    return data

if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]  # Example symbols
    data = fetch_yahoo_key_stats(symbols)
    insert_alternative_data(data)
    print("Key statistics data inserted into alternative_data table.")
    