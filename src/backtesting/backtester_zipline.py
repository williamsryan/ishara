from zipline.api import order, record, symbol, schedule_function, date_rules, time_rules
from zipline import run_algorithm
from zipline.utils.calendar_utils import get_calendar
from zipline.data.bundles import register
from zipline.data.bundles.core import ingest
from zipline.assets.asset_writer import AssetDBWriter
from zipline.assets import AssetFinder
from sqlalchemy import create_engine
import pandas as pd
import datetime as dt
from src.utils.database import fetch_data

class BacktesterZipline:
    def __init__(self, symbols, start_date, end_date, strategy, capital=100000):
        """
        Initialize the BacktesterZipline.

        Args:
            symbols (list): List of stock symbols.
            start_date (str): Start date (YYYY-MM-DD).
            end_date (str): End date (YYYY-MM-DD).
            strategy (BaseStrategy): User-defined trading strategy.
            capital (float): Initial capital for the backtest.
        """
        self.symbols = symbols
        self.start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
        self.strategy = strategy
        self.capital = capital
        self.data = None

    def fetch_historical_data(self):
        """
        Fetch historical data from the `historical_market_data` table.
        """
        query = f"""
            SELECT datetime, symbol, open, high, low, close, volume
            FROM historical_market_data
            WHERE symbol IN ({', '.join([f"'{s}'" for s in self.symbols])})
            AND datetime BETWEEN '{self.start_date}' AND '{self.end_date}'
            ORDER BY datetime
        """
        data = fetch_data(query)
        if data.empty:
            raise ValueError("No data available for the specified symbols and date range.")

        # Ensure data is indexed by normalized datetime and symbol
        data["datetime"] = pd.to_datetime(data["datetime"], utc=True)  # Ensure UTC alignment
        data["datetime"] = data["datetime"].dt.tz_convert(None)  # Convert to timezone-naive
        data["datetime"] = data["datetime"].dt.normalize()  # Remove time component
        data.set_index(["datetime", "symbol"], inplace=True)
        self.data = data

    def _create_asset_finder(self):
        """
        Create an AssetFinder with metadata stored in an in-memory SQLite database.
        """
        print("Generating asset metadata...")

        # Create asset metadata DataFrame
        asset_metadata = pd.DataFrame({
            "sid": range(len(self.symbols)),  # Asset IDs
            "symbol": self.symbols,
            "asset_name": self.symbols,
            "start_date": [pd.Timestamp(self.start_date)] * len(self.symbols),
            "end_date": [pd.Timestamp(self.end_date)] * len(self.symbols),
            "exchange": ["NYSE"] * len(self.symbols),
        })

        print(f"Asset metadata:\n{asset_metadata}")

        # Create an in-memory SQLite database
        engine = create_engine("sqlite:///:memory:")

        # Write metadata to the in-memory database
        writer = AssetDBWriter(engine)
        writer.write(asset_metadata)

        # Return an AssetFinder connected to the in-memory database
        return AssetFinder(engine)

    def _register_custom_bundle(self):
        """
        Register a custom Zipline data bundle using the `self.data` DataFrame.
        """
        # Get the trading calendar
        trading_calendar = get_calendar("XNYS")
        all_sessions = trading_calendar.sessions_in_range(self.start_date, self.end_date + pd.Timedelta(days=1))
        all_sessions = all_sessions.tz_localize(None)  # Ensure sessions are timezone-naive

        # Synchronize all_sessions with symbol_data
        valid_sessions = self.data.index.get_level_values(0).unique()
        all_sessions = all_sessions[all_sessions.isin(valid_sessions)]  # Keep only valid sessions

        # Create a mapping of symbols to integer SIDs
        symbol_to_sid = {symbol: i for i, symbol in enumerate(self.symbols)}

        def custom_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer,
                        adjustment_writer, calendar, start_session, end_session, cache,
                        show_progress, output_dir):
            """
            Custom bundle for ingesting data from a Pandas DataFrame.
            """
            daily_data = []
            for symbol, sid in symbol_to_sid.items():
                # Extract data for the symbol
                symbol_data = self.data.xs(symbol, level="symbol")
                if symbol_data.empty:
                    print(f"Warning: No data for symbol {symbol}")
                    continue

                # Align data with trading calendar
                symbol_data = symbol_data.reindex(all_sessions)
                symbol_data.index = symbol_data.index.tz_localize(None)  # Ensure timezone-naive index

                # Drop rows with missing values
                symbol_data = symbol_data.dropna(how="any")

                # Debugging: Validate no NaN rows remain
                if symbol_data.isna().any().any():
                    print(f"ERROR: NaN values found in symbol_data for SID {sid}:\n{symbol_data[symbol_data.isna().any(axis=1)]}")
                    raise ValueError(f"NaN values detected for SID {sid}.")

                # Debugging: Check data structure
                if sid == 0:
                    print(f"DEBUG: Full symbol_data for SID {sid}:\n{symbol_data}")

                # Validate alignment
                if not symbol_data.index.equals(all_sessions):
                    print(f"Alignment mismatch for SID {sid}.")
                    print(f"Index differences for SID {sid}:\n{symbol_data.index.difference(all_sessions)}")
                    print(f"Extra sessions in symbol_data for SID {sid}:\n{all_sessions.difference(symbol_data.index)}")
                    raise ValueError(f"Mismatch between symbol_data and all_sessions for SID {sid}.")

                # Add SID and reset index for writer compatibility
                symbol_data = symbol_data.reset_index()
                symbol_data["sid"] = sid

                daily_data.append((sid, symbol_data))

            # Debug final data structure
            print(f"DEBUG: Final daily_data structure:\n{daily_data}")

            # Write data to daily bar writer
            if not daily_data:
                raise ValueError("No valid data available for any symbols.")
            daily_bar_writer.write(
                daily_data,
                show_progress=show_progress,
            )
            adjustment_writer.write()

        # Register the custom bundle
        register("custom_bundle", custom_bundle)

        # Ingest the bundle
        try:
            ingest("custom_bundle", show_progress=True)
        except Exception as e:
            print(f"Error during ingestion: {e}")
            raise

    def run(self):
        """
        Run the backtest with the provided strategy.
        """
        print("Fetching historical data...")
        self.fetch_historical_data()

        print("Registering custom data bundle...")
        self._register_custom_bundle()

        # Ensure the first trading day is naive
        first_trading_day = self.data.index.get_level_values(0).min()
        first_trading_day = first_trading_day.normalize()
        # print(f"First trading day (naive): {first_trading_day}")

        trading_calendar = get_calendar("XNYS")

        print("Running algorithm...")
        # Run the backtest
        results = run_algorithm(
            start=self.start_date,
            end=self.end_date,
            capital_base=self.capital,
            data_frequency="daily",
            initialize=self.strategy.initialize,
            handle_data=self.strategy.handle_data,
            trading_calendar=trading_calendar,
        )
        print("Backtest completed!")
        return results
    