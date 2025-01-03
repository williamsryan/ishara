import backtrader as bt
import pandas as pd
from datetime import datetime
from src.utils.database import fetch_as_dataframe, insert_backtest_results, insert_trade_logs
from src.backtesting.strategies.moving_avg import MovingAverageCrossover
from src.backtesting.strategies.momentum import MomentumStrategy
import plotly.graph_objects as go

class BacktestManager:
    """
    Manages backtesting execution and results visualization.
    """

    def __init__(self):
        self.results = None
        self.cerebro = bt.Cerebro()
        self.strategies = {
            "MovingAverageCrossover": MovingAverageCrossover,
            "MomentumStrategy": MomentumStrategy
        }

    def perform_backtest(self, strategy_input, symbols, start_date, end_date, cash=100000):
        """
        Perform backtesting using the specified strategy and symbols.

        Args:
            strategy_input (str or callable): Name of the strategy or a custom strategy function.
            symbols (list): List of symbols to backtest.
            start_date (str): Start date (YYYY-MM-DD).
            end_date (str): End date (YYYY-MM-DD).
            cash (float): Initial cash for the portfolio.

        Returns:
            dict: Backtest results including performance and trades data.
        """
        # Initialize Backtrader
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.set_cash(cash)
        self.cerebro.broker.setcommission(commission=0.001)

        # Add data for each symbol
        for symbol in symbols:
            data = self._fetch_data(symbol, start_date, end_date)
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol} between {start_date} and {end_date}.")
            data_feed = self._prepare_backtrader_feed(data, symbol)
            self.cerebro.adddata(data_feed)

        # Add the selected strategy
        if isinstance(strategy_input, str):
            strategy_class = self.strategies.get(strategy_input)
            if not strategy_class:
                raise ValueError(f"Strategy {strategy_input} not found.")
            self.cerebro.addstrategy(strategy_class)
        else:
            strategy_function = self._wrap_dynamic_strategy(strategy_input)
            self.cerebro.addstrategy(strategy_function)

        try:
            print("🚀 Starting backtest...")
            strategies = self.cerebro.run()
            print(f"✅ Backtest completed. Strategies returned: {strategies}")
        except Exception as e:
            print(f"❌ Error during cerebro.run(): {e}")
            raise

        portfolio_value = self.cerebro.broker.getvalue()

        # Process and save results
        return self._process_results(strategy_input, symbols, start_date, end_date, cash)
    
    def _fetch_data(self, symbol, start_date, end_date):
        """
        Fetch historical market data for a given symbol and date range.
        """
        query = f"""
        SELECT datetime, open, high, low, close, volume
        FROM historical_market_data
        WHERE symbol = '{symbol}'
        AND datetime BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY datetime ASC
        """
        data = fetch_as_dataframe(query)
        data["datetime"] = pd.to_datetime(data["datetime"])  # Ensure datetime conversion
        return data
    
    def _prepare_backtrader_feed(self, data, symbol):
        """
        Convert a DataFrame into a Backtrader-compatible data feed.
        """
        return bt.feeds.PandasData(
            dataname=data,
            datetime="datetime",
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            timeframe=bt.TimeFrame.Days,
            name=symbol,
        )
    
    def _wrap_dynamic_strategy(self, strategy_func):
        """
        Wraps a dynamic strategy function into a Backtrader-compatible strategy class.
        """
        class DynamicStrategy(bt.Strategy):
            def __init__(self):
                self.strategy_func = strategy_func

            def next(self):
                # Fetch current bar data
                current_data = {
                    field: getattr(self.datas[0], field)[0]
                    for field in ['datetime', 'open', 'high', 'low', 'close', 'volume']
                }
                print(f"📊 Current data: {current_data}")

                # Call the user-defined strategy function
                decision = self.strategy_func(current_data)

                # Execute buy/sell based on the decision
                if decision.get("buy"):
                    print("📈 Buy signal detected.")
                    self.buy()
                elif decision.get("sell"):
                    print("📉 Sell signal detected.")
                    self.sell()

        return DynamicStrategy

    def _process_results(self, strategy_name, symbols, start_date, end_date, cash):
        trades = []
        portfolio_value = self.cerebro.broker.getvalue()
        pnl = portfolio_value - cash

        for strat in self.cerebro.runstrats:
            strategy = strat[0]
            if hasattr(strategy, "orders") and isinstance(strategy.orders, list):
                print(f"📈 Processing trades for strategy '{strategy_name}'...")
                for order in strategy.orders:
                    # print(f"DEBUG: Trade details - {order}")
                    # print(f"DEBUG: Price: {order.get("price_per_share")}")
                    trades.append((
                        strategy_name,
                        order.get("symbol"),
                        order.get("action"),
                        order.get("quantity"),
                        order.get("price_per_share"),
                        order.get("datetime"),
                        order.get("pnl")
                    ))

        trades_df = pd.DataFrame(trades, columns=["strategy", "symbol", "action", "quantity", "price", "datetime", "pnl"])
        if not trades_df.empty:
            try:
                insert_trade_logs(trades_df.to_dict("records"))  # Insert as list of dicts
                print(f"✅ Logged {len(trades_df)} trades into the database.")
            except Exception as e:
                print(f"❌ Error inserting data into trade_logs: {e}")

        # Prepare backtest results
        backtest_results = [{
            "strategy": strategy_name,
            "symbol": ", ".join(symbols),
            "start_date": start_date,
            "end_date": end_date,
            "initial_value": cash,
            "final_value": portfolio_value,
            "return_percentage": round((pnl / cash) * 100, 4),
        }]

        # Insert backtest results into the database
        try:
            insert_backtest_results(backtest_results)
            print(f"✅ Backtest results saved for strategy '{strategy_name}'.")
        except Exception as e:
            print(f"❌ Error inserting data into backtest_results: {e}")

        print(f"Final Portfolio Value: ${portfolio_value:.2f}")
        print(f"Total PnL: ${pnl:.2f}")

        return {
            "trades": trades,
            "portfolio_value": portfolio_value,
            "pnl": pnl,
        }

    def _store_results(self, results):
        """
        Save backtest results to the database.
        """
        data_to_insert = [
            (
                result["strategy"],
                result["symbol"],
                result["start_date"],
                result["end_date"],
                result["initial_value"],
                result["final_value"],
                result["return_percentage"]
            )
            for result in results
        ]
        insert_backtest_results(data_to_insert)

    def generate_performance_chart(self):
        """
        Generates a performance chart for the backtest.
        """
        if self.results is None:
            raise ValueError("No backtest results available for visualization.")

        fig = go.Figure()
        for symbol, group in self.results.groupby("symbol"):
            fig.add_trace(
                go.Scatter(
                    x=group["datetime"],
                    y=(1 + group["returns"]).cumprod(),
                    mode="lines",
                    name=symbol,
                    line=dict(width=2)
                )
            )

        fig.update_layout(
            title="Backtest Performance",
            xaxis_title="Date",
            yaxis_title="Cumulative Returns",
            template="plotly_white"
        )
        return fig

    def generate_trades_chart(self):
        """
        Generates a trades chart to visualize entries and exits.
        """
        if self.results is None:
            raise ValueError("No backtest results available for visualization.")

        fig = go.Figure()
        for symbol, group in self.results.groupby("symbol"):
            fig.add_trace(
                go.Scatter(
                    x=group["datetime"],
                    y=group["close"],
                    mode="markers",
                    name=f"{symbol} Trades",
                    marker=dict(size=6, symbol="circle")
                )
            )

        fig.update_layout(
            title="Trades Overview",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )
        return fig

    def generate_trades_table(self):
        """
        Generates a table of trade results.
        """
        if self.results is None:
            raise ValueError("No backtest results available for visualization.")

        trades = self.results[["datetime", "symbol", "close", "returns"]].copy()
        trades.rename(
            columns={
                "datetime": "Date",
                "symbol": "Symbol",
                "close": "Price",
                "returns": "Daily Return"
            },
            inplace=True
        )
        trades["Daily Return"] = trades["Daily Return"].round(4)
        return trades
    