import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objs as go
from src.utils.database import connect_to_db
from threading import Thread
from src.fetchers.alpaca_realtime import start_stream

# Initialize the Dash app with Bootstrap for better aesthetics
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
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
    # Title
    dbc.Row([
        dbc.Col(html.H1("📊 Ishara Trading Dashboard", className="text-center my-4"))
    ]),

    # Explanation Section
    dbc.Row([
        dbc.Col(
            dcc.Markdown("""
            **Welcome to Ishara Dashboard**  
            This dashboard displays real-time, historical, and alternative data sources.  
            - Use the **Dropdowns** to filter data by symbols or sources.  
            - Toggle **Data Sources** for better insights.  
            - Select specific **metrics** to visualize trends.  
            """, className="mb-4"),
            width=12
        )
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
            html.Label("Select Data Metric (for Alternative Data):"),
            dcc.Dropdown(
                id="metric-selector",
                options=[
                    {'label': 'Sentiment Score', 'value': 'sentiment_score'}
                ],
                multi=False
            )
        ], width=4),
    ]),

    # Graph Display
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='data-graph', style={"height": "500px"})
        ], width=12),
    ]),

    # Refresh Interval
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Refresh every 5 seconds
        n_intervals=0
    ),
], fluid=True)

# Callback to update graph dynamically
@app.callback(
    Output('data-graph', 'figure'),
    [
        Input('data-source', 'value'),
        Input('interval-component', 'n_intervals'),
        Input('ticker-input', 'value'),
        Input('metric-selector', 'value')
    ]
)
def update_graph(table, n_intervals, ticker_input, selected_metric):
    """
    Update graph based on user inputs and selected data source.
    """
    data = fetch_data(table)
    if data.empty:
        return {"layout": {"title": "No Data Available"}}

    # Filter by ticker symbols if provided
    if ticker_input:
        tickers = [t.strip().upper() for t in ticker_input.split(",")]
        data = data[data['symbol'].isin(tickers)]

    # Dynamic rendering for Alternative Data
    if table == "alternative_data":
        if selected_metric and selected_metric in data['metric'].unique():
            data = data[data['metric'] == selected_metric]
        figure = {
            'data': [
                go.Scatter(
                    x=data['datetime'],
                    y=data['value'],
                    mode='lines+markers',
                    text=data['details'],  # Add tooltips for details
                    name=f"{row['source']} ({row['symbol']})"
                ) for _, row in data.iterrows()
            ],
            'layout': go.Layout(
                title="Alternative Data Trends",
                xaxis={'title': 'Datetime'},
                yaxis={'title': 'Metric Value'},
                hovermode="closest",
                template="plotly_dark"
            )
        }
    elif table == "real_time_market_data":
        # Resample for OHLC
        ohlc_data = data.resample('1T', on='datetime')['price'].ohlc()
        ohlc_data.reset_index(inplace=True)
        figure = {
            'data': [
                go.Candlestick(
                    x=ohlc_data['datetime'],
                    open=ohlc_data['open'],
                    high=ohlc_data['high'],
                    low=ohlc_data['low'],
                    close=ohlc_data['close'],
                    name="OHLC"
                )
            ],
            'layout': go.Layout(
                title="Real-Time OHLC Data",
                xaxis={'title': 'Datetime'},
                yaxis={'title': 'Price'},
                template="plotly_dark"
            )
        }
    else:
        figure = {
            'data': [
                go.Scatter(
                    x=data['datetime'],
                    y=data[data.columns[1]],
                    mode='lines+markers',
                    name=data.columns[1]
                )
            ],
            'layout': go.Layout(
                title="Historical Market Data",
                xaxis={'title': 'Datetime'},
                yaxis={'title': data.columns[1]},
                template="plotly_dark"
            )
        }
    return figure

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
    