import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from src.utils.database import connect_to_db
from threading import Thread
from src.fetchers.alpaca_realtime import start_stream
import time

# Initialize the Dash app with Bootstrap for styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Ishara Trading Dashboard"

# Theme settings
THEMES = {
    "dark": dbc.themes.CYBORG,
    "light": dbc.themes.FLATLY
}

# Fetch data helper
def fetch_data(table, limit=1000):
    try:
        conn = connect_to_db()
        query = f"SELECT * FROM {table} ORDER BY datetime DESC LIMIT {limit}"
        data = pd.read_sql(query, conn)
        if not data.empty:
            data['datetime'] = pd.to_datetime(data['datetime'])
            return data
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# App Layout
app.layout = dbc.Container([
    # Title Row
    dbc.Row([
        dbc.Col(html.H1("📊 Ishara Trading Dashboard", className="text-center my-4"), width=12)
    ]),

    # Controls
    dbc.Row([
        dbc.Col([
            html.Label("Select Data Source:"),
            dcc.Dropdown(
                id="data-source",
                options=[
                    {'label': 'Alpaca Real-Time Data', 'value': 'real_time_market_data'},
                    {'label': 'Yahoo Finance Historical', 'value': 'yahoo_finance_data'},
                    {'label': 'Alternative Data (Google/Reddit)', 'value': 'alternative_data'}
                ],
                value='real_time_market_data',
                style={"margin-bottom": "15px"}
            ),

            html.Label("Choose Graph Style:"),
            dcc.RadioItems(
                id="graph-style",
                options=[
                    {'label': 'Line Graph', 'value': 'line'},
                    {'label': 'Candlestick', 'value': 'candlestick'},
                    {'label': 'Bar Chart', 'value': 'bar'}
                ],
                value='line',
                inline=True
            ),

            html.Label("Select Theme:"),
            dcc.RadioItems(
                id="theme-toggle",
                options=[
                    {'label': 'Light Theme', 'value': 'light'},
                    {'label': 'Dark Theme', 'value': 'dark'}
                ],
                value='dark',
                inline=True
            ),
        ], width=4),

        dbc.Col([
            html.Label("Enter Ticker Symbols (comma-separated):"),
            dcc.Input(id="ticker-input", type="text", placeholder="e.g., AAPL, MSFT", debounce=True),
            
            html.Label("Specify Timeframe:"),
            dcc.Dropdown(
                id="timeframe-selector",
                options=[
                    {"label": "Last 1 Day", "value": 1},
                    {"label": "Last 7 Days", "value": 7},
                    {"label": "Last 30 Days", "value": 30}
                ],
                value=7
            ),

            html.Br(),
            html.Button("Export as CSV", id="export-csv", className="btn btn-primary", style={"margin-right": "5px"}),
            html.Button("Export as JSON", id="export-json", className="btn btn-secondary")
        ], width=8)
    ]),

    html.Hr(),

    # Graph
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='main-graph', style={"height": "500px"})
        ], width=12),
    ]),

    # Interval for refresh
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Refresh every 5 seconds
        n_intervals=0
    ),

    # Hidden Div for data export
    dcc.Download(id="download-data")
], fluid=True)

# Callbacks
@app.callback(
    [Output('main-graph', 'figure'),
     Output('download-data', 'data')],
    [
        Input('data-source', 'value'),
        Input('ticker-input', 'value'),
        Input('graph-style', 'value'),
        Input('timeframe-selector', 'value'),
        Input('export-csv', 'n_clicks'),
        Input('export-json', 'n_clicks'),
        Input('interval-component', 'n_intervals')
    ],
    prevent_initial_call="initial_duplicate"
)
def update_dashboard(table, ticker_input, graph_style, timeframe, export_csv, export_json, n_intervals):
    """
    Update the main graph dynamically and handle data export.
    """
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Fetch Data
    data = fetch_data(table, limit=5000)
    if data.empty:
        return {"layout": {"title": "No Data Available"}}, None

    # Filter by ticker and timeframe
    if ticker_input:
        tickers = [t.strip().upper() for t in ticker_input.split(",")]
        data = data[data['symbol'].isin(tickers)]
    data = data[data['datetime'] > pd.Timestamp.now() - pd.Timedelta(days=timeframe)]

    # Prepare Graph
    if graph_style == "candlestick":
        graph_figure = {
            "data": [
                go.Candlestick(
                    x=data['datetime'],
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name=symbol
                )
                for symbol in data['symbol'].unique()
            ],
            "layout": go.Layout(
                title=f"{table} - Candlestick Chart",
                xaxis={"title": "Datetime"},
                yaxis={"title": "Price"}
            )
        }
    elif graph_style == "bar":
        graph_figure = {
            "data": [
                go.Bar(
                    x=data['datetime'],
                    y=data['price'],
                    name=symbol
                )
                for symbol in data['symbol'].unique()
            ],
            "layout": go.Layout(
                title=f"{table} - Bar Chart",
                xaxis={"title": "Datetime"},
                yaxis={"title": "Price"}
            )
        }
    else:
        graph_figure = {
            "data": [
                go.Scatter(
                    x=data['datetime'],
                    y=data['price'] if "price" in data.columns else data[data.columns[1]],
                    mode="lines",
                    name=symbol
                )
                for symbol in data['symbol'].unique()
            ],
            "layout": go.Layout(
                title=f"{table} - Line Graph",
                xaxis={"title": "Datetime"},
                yaxis={"title": "Price"}
            )
        }

    # Export Logic
    if trigger_id == "export-csv":
        return graph_figure, dcc.send_data_frame(data.to_csv, "exported_data.csv")
    elif trigger_id == "export-json":
        return graph_figure, dcc.send_data_frame(data.to_json, "exported_data.json")

    return graph_figure, None

def run_dashboard_with_stream():
    """
    Launch WebSocket streamer and dashboard together.
    """
    print("🚀 Starting Alpaca real-time streamer in the background...")
    stream_thread = Thread(target=start_stream)
    stream_thread.daemon = True
    stream_thread.start()

    print("🚀 Launching the Ishara Trading Dashboard...")
    app.run_server(debug=True)

if __name__ == '__main__':
    run_dashboard_with_stream()
    