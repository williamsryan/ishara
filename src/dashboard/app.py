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

# Fetch data helper
def fetch_data(table):
    try:
        conn = connect_to_db()
        query = f"SELECT * FROM {table} ORDER BY datetime DESC LIMIT 1000"
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
    dbc.Row([
        dbc.Col(html.H1("📊 Ishara Trading Dashboard", className="text-center my-4"), width=12)
    ]),

    # Feedback Row
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-feedback",
                type="circle",
                children=[
                    dcc.Markdown(id="search-feedback", children="🔍 Start by selecting a ticker and data source.")
                ]
            )
        ], width=12)
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
        ], width=4),

        dbc.Col([
            html.Label("Enter Ticker Symbols (comma-separated):"),
            dcc.Input(id="ticker-input", type="text", placeholder="e.g., AAPL, MSFT", debounce=True)
        ], width=4),

        dbc.Col([
            html.Label("Overlay Alternative Data:"),
            dcc.Dropdown(
                id="overlay-selector",
                options=[
                    {'label': 'Sentiment Score', 'value': 'sentiment_score'}
                ],
                multi=True,
                placeholder="Select overlays (optional)"
            )
        ], width=4),
    ]),

    html.Hr(),

    # Graph Panes
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='main-graph', style={"height": "500px"})
        ], width=8),
        dbc.Col([
            dcc.Graph(id='overlay-graph', style={"height": "500px"})
        ], width=4)
    ]),

    # Interval for refresh
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Refresh every 5 seconds
        n_intervals=0
    ),
], fluid=True)

# Callbacks
@app.callback(
    [Output('main-graph', 'figure'),
     Output('overlay-graph', 'figure'),
     Output('search-feedback', 'children')],
    [
        Input('data-source', 'value'),
        Input('ticker-input', 'value'),
        Input('overlay-selector', 'value'),
        Input('interval-component', 'n_intervals')
    ]
)
def update_graphs(table, ticker_input, overlays, n_intervals):
    """
    Update the main and overlay graphs dynamically.
    """
    feedback = "🔍 Searching..."
    time.sleep(0.5)  # Simulate a short loading time
    data = fetch_data(table)

    if data.empty:
        return {"layout": {"title": "No Data Available"}}, {}, "❌ No data available. Check the source."

    # Filter tickers
    if ticker_input:
        tickers = [t.strip().upper() for t in ticker_input.split(",")]
        data = data[data['symbol'].isin(tickers)]
        feedback = f"✅ Showing data for: {', '.join(tickers)}"

    # Prepare main graph
    main_fig = {
        'data': [
            go.Scatter(
                x=data['datetime'],
                y=data['price'] if 'price' in data.columns else data[data.columns[1]],
                mode='lines+markers',
                name=f"{symbol} Price"
            )
            for symbol in data['symbol'].unique()
        ],
        'layout': go.Layout(
            title="Price Data",
            xaxis={'title': 'Datetime'},
            yaxis={'title': 'Price'},
            template="plotly_dark"
        )
    }

    # Prepare overlay graph
    overlay_fig = {"data": [], "layout": go.Layout(title="Overlay Data", template="plotly_dark")}
    if overlays and table == 'alternative_data':
        overlay_data = fetch_data('alternative_data')
        overlay_data = overlay_data[overlay_data['metric'].isin(overlays)]
        overlay_fig = {
            'data': [
                go.Scatter(
                    x=overlay_data['datetime'],
                    y=overlay_data['value'],
                    mode='lines+markers',
                    name=f"{row['metric']} ({row['source']})"
                )
                for _, row in overlay_data.iterrows()
            ],
            'layout': go.Layout(
                title="Overlay: Alternative Data",
                xaxis={'title': 'Datetime'},
                yaxis={'title': 'Metric Value'},
                template="plotly_dark"
            )
        }

    return main_fig, overlay_fig, feedback

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
    