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
        self.initial_capital = 100000
        self.strategies = {
            "MovingAverageCrossover": MovingAverageCrossover,
            "MomentumStrategy": MomentumStrategy
        }

    def perform_backtest(self, strategy_input, symbols, start_date, end_date):
        """
        Perform backtesting using the specified strategy and symbols.

        Args:
            strategy_input (str or callable): Name of the strategy or a custom strategy function.
            symbols (list): List of symbols to backtest.
            start_date (str): Start date (YYYY-MM-DD).
            end_date (str): End date (YYYY-MM-DD).

        Returns:
            dict: Backtest results including performance and trades data.
        """
        # Initialize Backtrader
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.set_cash(self.initial_capital)
        self.cerebro.broker.setcommission(commission=0.001)

        # Add data for each symbol
        for symbol in symbols:
            data = self._fetch_data(symbol, start_date, end_date)
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol} between {start_date} and {end_date}.")
            # print(f"📊 Data preview for {symbol}:\n{data.head()}")
            # print(f"Data index type: {type(data.index[0])}")
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
        results = self._process_results(strategy_input, symbols, start_date, end_date, self.initial_capital)

        trades = [] 
        for trade in self.cerebro.broker.orders:
            trades.append({
                "symbol": trade.symbol,
                "price": trade.executed.price,
                "size": trade.executed.size,
                "datetime": trade.executed.dt,
                "pnl": trade.executed.pnl,
            })

        self.results = {
            "portfolio_value": portfolio_value,
            "pnl": portfolio_value - self.initial_capital,
            "trades": pd.DataFrame(trades),  # Include detailed trades
            "cumulative_returns": self._compute_cumulative_returns(),
        }

        return {
            "portfolio_value": portfolio_value,
            "pnl": self.results["pnl"],
            "trades": self.results["trades"],
            "cumulative_returns": self.results["cumulative_returns"],
        }
    
    def _fetch_data(self, symbol, start_date, end_date):
        query = f"""
        SELECT datetime, open, high, low, close, volume
        FROM historical_market_data
        WHERE symbol = '{symbol}'
        AND datetime BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY datetime ASC
        """
        data = fetch_as_dataframe(query)
        if data.empty or not set(["datetime", "open", "high", "low", "close", "volume"]).issubset(data.columns):
            raise ValueError(f"Invalid data for symbol {symbol}. Please check the database.")

        return data
    
    def _prepare_backtrader_feed(self, data, symbol):
        if not pd.api.types.is_datetime64_any_dtype(data["datetime"]):
            raise ValueError("The datetime column must be a valid datetime type.")

        data.set_index("datetime", inplace=True)
        return bt.feeds.PandasData(
            dataname=data,
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            timeframe=bt.TimeFrame.Minutes,
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
                try:
                    # Create a DataFrame from the current data
                    current_data = {
                        field: [getattr(self.datas[0], field)[0]]
                        for field in ["open", "high", "low", "close", "volume"]
                    }
                    current_data["datetime"] = [self.datas[0].datetime.datetime(0)]  # Wrap in list to create a DataFrame

                    # Convert to a DataFrame
                    current_df = pd.DataFrame(current_data)

                    # print(f"📊 Current data (DataFrame):\n{current_df}")

                    # Pass the DataFrame to the strategy function
                    decision = self.strategy_func(current_df)

                    # Explicitly handle Series or ambiguous values
                    if isinstance(decision.get("buy"), pd.Series):
                        buy_signal = decision.get("buy").iloc[0]
                    else:
                        buy_signal = bool(decision.get("buy"))

                    if isinstance(decision.get("sell"), pd.Series):
                        sell_signal = decision.get("sell").iloc[0]
                    else:
                        sell_signal = bool(decision.get("sell"))

                    if buy_signal:
                        print("📈 Buy signal detected.")
                        self.buy()
                    elif sell_signal:
                        print("📉 Sell signal detected.")
                        self.sell()
                except Exception as e:
                    print(f"❌ Error processing next step in strategy: {e}")

        return DynamicStrategy

    def _process_results(self, strategy_name, symbols, start_date, end_date, cash):
        trades = []
        portfolio_value = self.cerebro.broker.getvalue()
        pnl = portfolio_value - cash

        if callable(strategy_name):
            strategy_name = strategy_name.__name__

        for strat in self.cerebro.runstrats:
            strategy = strat[0]
            if hasattr(strategy, "orders") and isinstance(strategy.orders, list):
                for order in strategy.orders:
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
                insert_trade_logs(trades_df.to_dict("records"))
                print(f"✅ Logged {len(trades_df)} trades into the database.")
            except Exception as e:
                print(f"❌ Error inserting data into trade_logs: {e}")

        backtest_results = [{
            "strategy": strategy_name,
            "symbol": ", ".join(symbols),
            "start_date": start_date,
            "end_date": end_date,
            "initial_value": cash,
            "final_value": portfolio_value,
            "return_percentage": round((pnl / cash) * 100, 4),
        }]

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
    
    def _compute_cumulative_returns(self):
        all_data = []
        for symbol in self.cerebro.datas:
            symbol_name = symbol.params.name
            data = {
                "datetime": [bt.num2date(dt) for dt in symbol.datetime.array],
                "close": symbol.close.array,
                "symbol": symbol_name,
            }
            df = pd.DataFrame(data)
            df["returns"] = df["close"].pct_change().fillna(0)
            df["cumulative_returns"] = (1 + df["returns"]).cumprod()
            all_data.append(df)

        # Concatenate all DataFrames
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

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
        if self.results is None or not isinstance(self.results.get("cumulative_returns"), pd.DataFrame):
            raise ValueError("No backtest results available for visualization or cumulative_returns is not a DataFrame.")

        cumulative_returns = self.results["cumulative_returns"]  # This should now be a DataFrame
        print(f"DEBUG: Type of cumulative_returns: {type(self.results['cumulative_returns'])}")

        fig = go.Figure()
        for symbol, group in cumulative_returns.groupby("symbol"):
            fig.add_trace(
                go.Scatter(
                    x=group["datetime"],
                    y=group["cumulative_returns"],
                    mode="lines",
                    name=f"{symbol} Cumulative Returns",
                    line=dict(width=2)
                )
            )

        fig.update_layout(
            title="Cumulative Returns",
            xaxis_title="Date",
            yaxis_title="Cumulative Returns",
            template="plotly_white",
            height=600,
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
    