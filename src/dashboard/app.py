import dash
from dash import dcc, html, Input, Output, State, ctx, dash_table
import pandas as pd
import plotly.graph_objs as go
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
    if not symbols:
        return html.Div("⚠️ Please select symbols to display data.")

    # Fetch data
    data = fetch_data(source, limit=1000)
    alt_data = fetch_data("alternative_data", limit=1000) if overlay_toggle else pd.DataFrame()

    # Handle default date range
    if not start_date or not end_date:
        start_date = data["datetime"].min()
        end_date = data["datetime"].max()

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if tab == "price-chart":
        # Build Price Chart
        figure = go.Figure()

        for symbol in symbols:
            symbol_data = data[(data["symbol"] == symbol) &
                               (data["datetime"] >= start_date) &
                               (data["datetime"] <= end_date)]

            # Determine the price column dynamically
            price_column = next((col for col in ["close", "price", "value", "last"] if col in symbol_data.columns), None)

            if not price_column:
                return html.Div("⚠️ No price column found in the data. Please check the data source.")

            # Plot the data
            figure.add_trace(go.Scatter(
                x=symbol_data["datetime"], y=symbol_data[price_column], mode="lines", name=f"{symbol} Price"
            ))

            # Overlay Alternative Data
            if not alt_data.empty:
                alt_symbol_data = alt_data[(alt_data["symbol"] == symbol) &
                                           (alt_data["datetime"] >= start_date) &
                                           (alt_data["datetime"] <= end_date)]
                figure.add_trace(go.Scatter(
                    x=alt_symbol_data["datetime"], y=alt_symbol_data["value"], mode="lines", 
                    name=f"{symbol} Alt Data", yaxis="y2"
                ))

        figure.update_layout(
            title="Price and Alternative Data Overlay",
            yaxis=dict(title="Price"),
            yaxis2=dict(title="Alternative Data", overlaying="y", side="right"),
            legend=dict(title="Symbols")
        )
        return dcc.Graph(figure=figure)

    elif tab == "alternative-data":
        if alt_data.empty:
            return html.Div("⚠️ No alternative data available.")
        
        # Alternative Data Table
        return dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in alt_data.columns],
            data=alt_data.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
            filter_action="native",
            sort_action="native",
            page_size=10
        )

    elif tab == "table-view":
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
    