from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from dash_ace import DashAceEditor
from src.utils.database import fetch_as_dataframe
from src.backtesting.backtester import BacktestManager

# Predefined strategies
PREDEFINED_STRATEGIES = {
    "MovingAverageCrossover": """# Simple Moving Average Crossover Strategy
def MovingAverageCrossover(data):
    import pandas as pd

    # Convert data to DataFrame if necessary
    if isinstance(data, dict):
        data = pd.DataFrame(data)

    # Calculate short-term and long-term moving averages
    short_ma = data['close'].rolling(10).mean()
    long_ma = data['close'].rolling(30).mean()

    # Generate buy and sell signals
    buy_signal = short_ma > long_ma
    sell_signal = short_ma <= long_ma

    # Return buy/sell signals
    return {"buy": buy_signal, "sell": sell_signal}
""",
    "MomentumStrategy": """# Momentum Strategy
def MomentumStrategy(data):
    # Calculate returns
    returns = data['close'].pct_change()
    
    # Generate buy and sell signals
    buy_signal = returns > 0.01  # Example threshold
    sell_signal = returns <= 0.01
    
    # Return buy/sell signal as a boolean mask
    return buy_signal, sell_signal
"""
}

class StrategyEditor:
    @staticmethod
    def layout():
        """
        Layout for the Strategy Editor tab.
        """
        return html.Div([
            # Strategy Selector Dropdown
            html.Div([
                html.Label("Select Predefined Strategy"),
                dcc.Dropdown(
                    id="strategy-selector",
                    options=[{"label": name, "value": name} for name in PREDEFINED_STRATEGIES.keys()],
                    placeholder="Select a predefined strategy",
                    style={"width": "100%"}
                ),
            ], className="mb-3"),

            # Strategy Editor Section
            DashAceEditor(
                id="strategy-editor",
                value="",
                mode="python",
                theme="monokai",
                tabSize=4,
                enableBasicAutocompletion=True,
                enableLiveAutocompletion=True,
                placeholder="Write your strategy...",
                style={"width": "100%", "height": "300px"},
            ),
            html.Div([
                html.Label("Select Symbols for Backtesting"),
                dcc.Dropdown(
                    id="backtest-symbol-selector",
                    options=[],  # Will be dynamically populated
                    multi=True,
                    placeholder="Select symbols",
                    style={"width": "100%"}
                ),
            ]),
            dbc.Button("Run Backtest", id="run-backtest", color="primary", className="mt-3"),
            dcc.Loading(
                id="backtest-loading",
                type="circle",
                children=html.Div(id="backtest-results", className="mt-3")
            )
        ])

    @staticmethod
    @callback(
        Output("strategy-editor", "value"),
        Input("strategy-selector", "value")
    )
    def update_editor_with_predefined_strategy(selected_strategy):
        """
        Update the editor with the code of the selected predefined strategy.
        """
        if selected_strategy:
            return PREDEFINED_STRATEGIES[selected_strategy]
        return ""

    @staticmethod
    @callback(
        Output("backtest-symbol-selector", "options"),
        [Input("strategy-editor", "value")]
    )
    def update_symbol_options(_):
        """
        Populate the symbol dropdown options dynamically.
        """
        try:
            symbols = [{"label": symbol, "value": symbol} for symbol in fetch_as_dataframe(
                "SELECT DISTINCT symbol FROM historical_market_data"
            )["symbol"].tolist()]
            return symbols
        except Exception as e:
            print(f"❌ Error fetching symbol options: {str(e)}")
            return []

    @staticmethod
    @callback(
        Output("backtest-results", "children"),
        [Input("run-backtest", "n_clicks")],
        [
            State("strategy-selector", "value"),
            State("strategy-editor", "value"),
            State("backtest-symbol-selector", "value"),
            State("date-picker", "start_date"),
            State("date-picker", "end_date"),
        ],
    )
    def run_backtest(n_clicks, selected_strategy, strategy_code, symbols, start_date, end_date):
        """
        Execute the backtest and display results.
        """
        if not n_clicks:
            return html.Div("⚠️ Please click 'Run Backtest' to start.", className="text-warning p-3")

        if not symbols or not start_date or not end_date:
            return html.Div("⚠️ Please provide all inputs to run the backtest.", className="text-warning")

        try:
            # Load predefined strategy code if a strategy is selected
            if selected_strategy and selected_strategy in PREDEFINED_STRATEGIES:
                strategy_code = PREDEFINED_STRATEGIES[selected_strategy]

            # Validate the strategy code
            strategy_namespace = {}
            exec(strategy_code, {}, strategy_namespace)
            # Extract the strategy function
            strategy_function = strategy_namespace.get("strategy") or strategy_namespace.get(selected_strategy)

            if not callable(strategy_function):
                raise ValueError("The strategy must define a valid 'strategy' function.")

            # Perform the backtest
            backtest_manager = BacktestManager()
            results = backtest_manager.perform_backtest(strategy_function, symbols, start_date, end_date)

            # print(f"DEBUG: Backtest results: {results}")

            # Use BacktestManager for visualizations
            performance_chart = dcc.Graph(figure=backtest_manager.generate_performance_chart(results))
            trades_chart = dcc.Graph(figure=backtest_manager.generate_trades_chart(results))
            trades_table = dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in results["trades"].columns],
                data=results["trades"].to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left"},
            )

            return html.Div([
                dbc.Row(dbc.Col(performance_chart, width=12)),
                dbc.Row(dbc.Col(trades_chart, width=12)),
                dbc.Row(dbc.Col(trades_table, width=12))
            ])
        except Exception as e:
            print(f"❌ Error running backtest: {str(e)}")
            return html.Div(f"❌ Error running backtest: {str(e)}", className="text-danger p-3")
        