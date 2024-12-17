import dash
from dash import dcc, html, Input, Output, State, ctx, dash_table
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from src.utils.database import connect_to_db
from threading import Thread
from src.fetchers.alpaca_realtime import start_stream

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "📊 Ishara Trading Platform"

# Helper to fetch data
def fetch_data(table, limit=1000):
    try:
        engine = connect_to_db()
        query = f"SELECT * FROM {table} ORDER BY datetime DESC LIMIT {limit}"
        
        # Debugging: Print the SQL query
        print(f"🔍 Running query: {query}")
        
        data = pd.read_sql(query, con=engine)  # Ensure engine is SQLAlchemy compatible
        if not data.empty:
            data["datetime"] = pd.to_datetime(data["datetime"])
            return data
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame()

# Layout
app.layout = dbc.Container(fluid=True, children=[
    # Header
    dbc.Row([
        dbc.Col(html.H2("📊 Ishara Trading Dashboard", className="text-center text-light bg-dark p-3"), width=12)
    ]),

    # Controls and Sidebar
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("User Controls", className="mb-3"),

                # Data Source Dropdown
                html.Label("Select Data Source"),
                dcc.Dropdown(
                    id="data-source",
                    options=[
                        {"label": "Real-Time Data", "value": "real_time_market_data"},
                        {"label": "Yahoo Finance", "value": "yahoo_finance_data"},
                        {"label": "Alternative Data", "value": "alternative_data"}
                    ],
                    value="real_time_market_data",
                    clearable=True
                ),

                # Symbol Selector
                html.Label("Select Symbols"),
                dcc.Dropdown(
                    id="symbol-selector",
                    multi=True,
                    placeholder="Select symbols (e.g., AAPL, MSFT)"
                ),

                # Toggle Alternative Data Overlay
                dbc.Checklist(
                    options=[{"label": "Overlay Alternative Data", "value": 1}],
                    id="overlay-toggle",
                    switch=True
                ),

                # Time Range Picker
                html.Label("Select Time Range"),
                dcc.DatePickerRange(
                    id="date-picker",
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    display_format="YYYY-MM-DD"
                ),

                # Tools
                html.Button("View Trends", id="view-trends-btn", className="btn btn-primary mb-2"),
                html.Button("Calculate Moving Average", id="moving-average-btn", className="btn btn-secondary mb-2")
            ], className="bg-light p-3 rounded")
        ], width=2),

        # Main Content Tabs
        dbc.Col([
            dcc.Tabs(id="tabs", value="price-chart", children=[
                dcc.Tab(label="📈 Price Chart", value="price-chart"),
                dcc.Tab(label="📊 Alternative Data", value="alternative-data"),
                dcc.Tab(label="🗃 Table View", value="table-view"),
            ]),
            html.Div(id="tab-content", className="p-3")
        ], width=10),
    ])
])

# Callbacks
@app.callback(
    [Output("symbol-selector", "options"), Output("symbol-selector", "value")],
    Input("data-source", "value")
)
def update_symbols(source):
    data = fetch_data(source, limit=1000)
    if data.empty:
        return [], []
    symbols = [{"label": symbol, "value": symbol} for symbol in data["symbol"].unique()]
    return symbols, [symbols[0]["value"]] if symbols else []

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("data-source", "value"), Input("symbol-selector", "value"),
     Input("date-picker", "start_date"), Input("date-picker", "end_date"),
     Input("overlay-toggle", "value")]
)
def update_content(tab, source, symbols, start_date, end_date, overlay_toggle):
    # Always ensure symbols are selected
    if not symbols:
        return html.Div("⚠️ Please select symbols to display data.")

    # Handle default date range
    def get_default_date_range(df):
        return df["datetime"].min(), df["datetime"].max()

    # Handle fetching price or overlay data
    data = fetch_data(source, limit=1000) if tab in ["price-chart", "table-view"] else pd.DataFrame()
    alt_data = fetch_data("alternative_data", limit=1000) if tab == "alternative-data" or overlay_toggle else pd.DataFrame()

    if tab == "price-chart":
        # Default date range
        if data.empty:
            return html.Div("⚠️ No data available for the selected source or symbols.")

        start_date = start_date or get_default_date_range(data)[0]
        end_date = end_date or get_default_date_range(data)[1]
        start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)

        # Create subplots: Rows = 2 (Price/Moving Avg + Volume)
        figure = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1,
                            subplot_titles=("Price & Moving Averages", "Volume Trends"))

        for symbol in symbols:
            # Filter the data for this symbol and time range
            symbol_data = data[(data["symbol"] == symbol) &
                            (data["datetime"] >= start_date) &
                            (data["datetime"] <= end_date)]

            # Determine the price column dynamically
            price_column = next((col for col in ["close", "price", "value", "last"] if col in symbol_data.columns), None)
            if not price_column:
                continue

            # Calculate Moving Averages for Buy/Sell Signals
            symbol_data["SMA_50"] = symbol_data[price_column].rolling(window=50).mean()
            symbol_data["SMA_200"] = symbol_data[price_column].rolling(window=200).mean()

            # Plot Price Line
            figure.add_trace(
                go.Scatter(
                    x=symbol_data["datetime"], 
                    y=symbol_data[price_column],
                    mode="lines", 
                    name=f"{symbol} Price",
                    line=dict(color="blue")
                ), row=1, col=1
            )

            # Plot Moving Averages
            figure.add_trace(
                go.Scatter(
                    x=symbol_data["datetime"], 
                    y=symbol_data["SMA_50"],
                    mode="lines", 
                    name=f"{symbol} SMA 50",
                    line=dict(color="orange", dash="dot")
                ), row=1, col=1
            )

            figure.add_trace(
                go.Scatter(
                    x=symbol_data["datetime"], 
                    y=symbol_data["SMA_200"],
                    mode="lines", 
                    name=f"{symbol} SMA 200",
                    line=dict(color="red", dash="dot")
                ), row=1, col=1
            )

            # Add Buy/Sell Markers (SMA crossover)
            crossover = symbol_data[(symbol_data["SMA_50"] > symbol_data["SMA_200"])]
            figure.add_trace(
                go.Scatter(
                    x=crossover["datetime"], 
                    y=crossover[price_column],
                    mode="markers",
                    name=f"{symbol} Buy Signal",
                    marker=dict(color="green", size=10, symbol="triangle-up")
                ), row=1, col=1
            )

            # Add Volume Chart
            if "volume" in symbol_data.columns:
                figure.add_trace(
                    go.Bar(
                        x=symbol_data["datetime"],
                        y=symbol_data["volume"],
                        name=f"{symbol} Volume",
                        marker=dict(color="gray", opacity=0.6)
                    ), row=2, col=1
                )

        # Layout Improvements
        figure.update_layout(
            title="Price, Moving Averages, and Volume Trends",
            height=700,
            xaxis=dict(title="DateTime", rangeslider=dict(visible=True)),
            yaxis=dict(title="Price", showgrid=True),
            yaxis2=dict(title="Volume"),
            hovermode="x unified",
            legend=dict(x=0, y=1.2, orientation="h"),
            template="plotly_dark"  # Switch to a sleek dark theme
        )

        return dcc.Graph(figure=figure)

    elif tab == "alternative-data":
        # Fetch and display Alternative Data Table
        if alt_data.empty:
            return html.Div("⚠️ No alternative data available for the selected symbols.")

        alt_data_display = alt_data.rename(columns={
            "source": "Source",
            "symbol": "Symbol",
            "datetime": "Datetime",
            "metric": "Metric",
            "value": "Value",
            "details": "Details"
        })
        alt_data_display["Datetime"] = alt_data_display["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

        return html.Div([
            html.H5("Alternative Data Table", className="mb-3"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in alt_data_display.columns],
                data=alt_data_display.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left", "padding": "5px", "whiteSpace": "normal", "height": "auto"
                },
                style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                style_data_conditional=[
                    {"if": {"column_id": "Value", "filter_query": "{Value} < 0"}, "color": "red"},
                    {"if": {"column_id": "Value", "filter_query": "{Value} >= 0"}, "color": "green"}
                ],
                filter_action="native",
                sort_action="native",
                page_size=10
            )
        ])

    elif tab == "table-view":
        if data.empty:
            return html.Div("⚠️ No data available for the selected source or symbols.")

        return dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
            filter_action="native",
            sort_action="native",
            page_size=10
        )

    return html.Div("⚠️ Please select a valid tab.")

# Run Streamer
def run_dashboard_with_stream():
    stream_thread = Thread(target=start_stream)
    stream_thread.daemon = True
    stream_thread.start()
    app.run_server(debug=True)

if __name__ == "__main__":
    run_dashboard_with_stream()
