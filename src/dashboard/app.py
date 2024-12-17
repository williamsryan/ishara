import dash
from dash import dcc, html, Input, Output, State, ctx
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from threading import Thread
from src.utils.database import connect_to_db
from src.fetchers.alpaca_realtime import start_stream

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "📊 Ishara Trading Platform"

# Fetch Data Helper
def fetch_data(table, limit=1000):
    try:
        engine = connect_to_db()
        if not table:
            raise ValueError("No table name provided.")
        query = f"SELECT * FROM {table} ORDER BY datetime DESC LIMIT {limit}"
        data = pd.read_sql(query, engine)
        if not data.empty:
            data["datetime"] = pd.to_datetime(data["datetime"])
            return data
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame()

# Layout
app.layout = dbc.Container(fluid=True, children=[
    # Navbar
    dbc.Row([
        dbc.Col(html.H2("Ishara Trading Dashboard", className="text-center text-light bg-dark p-3"), width=12)
    ]),

    # Main Row
    dbc.Row([
        # Sidebar
        dbc.Col([
            html.Div([
                html.H4("Controls", className="mb-3"),

                # Data Source Dropdown
                html.Label("Data Source"),
                dcc.Dropdown(
                    id="data-source",
                    options=[
                        {"label": "Real-Time Data", "value": "real_time_market_data"},
                        {"label": "Yahoo Finance", "value": "yahoo_finance_data"},
                        {"label": "Alternative Data", "value": "alternative_data"}
                    ],
                    value="real_time_market_data"
                ),

                # Symbol Selector
                html.Label("Select Symbols"),
                dcc.Dropdown(
                    id="symbol-selector",
                    multi=True,
                    placeholder="e.g., AAPL, MSFT, GOOGL"
                ),

                # Time Range Selector
                html.Label("Select Time Range"),
                dcc.Slider(
                    id="time-range",
                    min=1, max=30, step=1,
                    marks={1: "1D", 7: "7D", 14: "14D", 30: "30D"},
                    value=7
                ),

                # Graph Style
                html.Label("Graph Style"),
                dcc.RadioItems(
                    id="graph-style",
                    options=[
                        {"label": "Line", "value": "line"},
                        {"label": "Candlestick", "value": "candlestick"}
                    ],
                    value="line", inline=True
                ),

                # Buttons
                html.Div([
                    html.Button("Run Backtest", id="run-backtest", className="btn btn-primary mt-3"),
                ]),
            ], className="bg-light p-3 rounded"),
        ], width=2),

        # Main Content Area
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Div("Streaming Status: ", style={"fontWeight": "bold", "display": "inline-block"}),
                    html.Div(id="stream-status", style={"display": "inline-block", "color": "green", "marginLeft": "10px"})
                ])
            ], className="mb-3"),

            dbc.Row([
                dcc.Tabs(id="tabs", value="price-tab", children=[
                    dcc.Tab(label="Price & Volume", value="price-tab"),
                    dcc.Tab(label="Portfolio Overview", value="portfolio-tab"),
                    dcc.Tab(label="Alternative Data", value="alt-tab"),
                ]),
                html.Div(id="tab-content")
            ])
        ], width=10),
    ]),

    # Interval for updates
    dcc.Interval(id="interval", interval=5000, n_intervals=0)
])

# Callbacks
@app.callback(
    [Output("symbol-selector", "options"),
     Output("symbol-selector", "value")],
    Input("data-source", "value")
)
def update_symbols(source):
    data = fetch_data(source, limit=1000)
    if data.empty:
        return [], None
    symbols = [{"label": symbol, "value": symbol} for symbol in data["symbol"].unique()]
    return symbols, symbols[0]["value"] if symbols else None

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"),
     Input("data-source", "value"),
     Input("symbol-selector", "value"),
     Input("graph-style", "value"),
     Input("time-range", "value"),
     Input("interval", "n_intervals")]
)
def update_tab_content(tab, source, symbols, graph_style, days, n_intervals):
    # Ensure symbols is a list
    if isinstance(symbols, str):
        symbols = [symbols]
    if not symbols:
        return html.Div("⚠️ No symbols selected. Please choose symbols to display data.")

    # Fetch and filter data
    data = fetch_data(source, limit=1000)
    if data.empty:
        return html.Div("⚠️ No data available for the selected source.")

    # Validate required columns exist
    required_columns = ["datetime", "symbol", "price"]
    for col in required_columns:
        if col not in data.columns:
            return html.Div(f"⚠️ The selected data source is missing the '{col}' column. Please check the source.")

    filtered_data = data[data["symbol"].isin(symbols)]
    filtered_data = filtered_data[filtered_data["datetime"] > pd.Timestamp.now() - pd.Timedelta(days=days)]

    if filtered_data.empty:
        return html.Div("⚠️ No data found for the selected symbols and time range.")

    # Price & Volume Tab
    if tab == "price-tab":
        figure = go.Figure()

        # Graph style
        if graph_style == "candlestick" and all(col in filtered_data.columns for col in ["open", "high", "low", "close"]):
            for symbol in symbols:
                sym_data = filtered_data[filtered_data["symbol"] == symbol]
                figure.add_trace(go.Candlestick(
                    x=sym_data["datetime"], open=sym_data["open"], high=sym_data["high"],
                    low=sym_data["low"], close=sym_data["close"], name=symbol
                ))
        else:
            for idx, symbol in enumerate(symbols):  # Add enumerate to track idx
                sym_data = filtered_data[filtered_data["symbol"] == symbol]
                figure.add_trace(go.Scatter(
                    x=sym_data["datetime"], y=sym_data["price"], mode="lines", name=symbol,
                    yaxis="y2" if idx > 0 else "y"  # Alternate between primary and secondary axes
                ))

        # Update layout to handle separate y-axes for multiple symbols
        figure.update_layout(
            title="Price & Volume",
            yaxis={"title": "Price", "side": "left"},
            yaxis2={"title": "Price (Secondary)", "overlaying": "y", "side": "right"},
            legend_title="Symbols",
            xaxis={"title": "Datetime"}
        )
        return dcc.Graph(figure=figure)

    # Portfolio Overview Tab
    elif tab == "portfolio-tab":
        stats = filtered_data.groupby("symbol").agg({"price": "last", "volume": "sum"})
        return html.Div([
            html.H4("Portfolio Overview"),
            html.Table([
                html.Tr([html.Th("Symbol"), html.Th("Latest Price"), html.Th("Total Volume")]),
                *[html.Tr([html.Td(symbol), html.Td(f"${row['price']:.2f}"), html.Td(f"{row['volume']:,}")])
                  for symbol, row in stats.iterrows()]
            ], className="table table-bordered table-striped")
        ])

    # Alternative Data Tab
    elif tab == "alt-tab":
        return html.Div("Alternative Data Visualization Coming Soon!")

@app.callback(
    Output("stream-status", "children"),
    Input("interval", "n_intervals")
)
def update_stream_status(n_intervals):
    return "Connected" if n_intervals % 2 == 0 else "Disconnected"

# Start Streamer
def run_dashboard_with_stream():
    stream_thread = Thread(target=start_stream)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard_with_stream()
