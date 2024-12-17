import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from src.utils.database import connect_to_db
from threading import Thread
from src.fetchers.alpaca_realtime import start_stream

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Ishara Trading Dashboard"

def fetch_data(table):
    """
    Fetch data from the specified database table.
    """
    if not table:  # Check for invalid table names
        print("⚠️ Invalid table name provided.")
        return pd.DataFrame()

    conn = connect_to_db()
    try:
        query = f"SELECT * FROM {table} ORDER BY datetime DESC LIMIT 1000"
        return pd.read_sql(query, conn)
    except Exception as e:
        print(f"❌ Error fetching data from {table}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# App Layout
app.layout = html.Div([
    html.H1("📊 Ishara Trading Dashboard", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id="data-source",
        options=[
            {'label': 'Alpaca Real-Time Data', 'value': 'real_time_market_data'},
            {'label': 'Yahoo Finance Historical', 'value': 'yahoo_finance_data'},
            {'label': 'Alternative Data (Google/Reddit)', 'value': 'alternative_data'}
        ],
        value='real_time_market_data',  # Default value
        style={"width": "50%", "margin": "auto"}
    ),

    dcc.Graph(id='data-graph'),

    dcc.Interval(
        id='interval-component',
        interval=5000,  # Refresh every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    Output('data-graph', 'figure'),
    [Input('data-source', 'value'), Input('interval-component', 'n_intervals')]
)
def update_graph(table, n_intervals):
    """
    Update the graph based on the selected data source and refresh interval.
    """
    data = fetch_data(table)
    if data.empty:
        return {"layout": {"title": "No Data Available"}}

    if table == 'alternative_data':
        # Plot multiple lines for different sources
        figure = {
            'data': [],
            'layout': go.Layout(
                title="Alternative Data Trends",
                xaxis={'title': 'Datetime'},
                yaxis={'title': 'Value'},
                template="plotly_dark"
            )
        }

        for metric in data['metric'].unique():
            filtered = data[data['metric'] == metric]
            figure['data'].append(
                go.Scatter(
                    x=filtered['datetime'],
                    y=filtered['value'],
                    mode='lines+markers',
                    name=metric
                )
            )
    else:
        # Default candlestick chart for real-time and Yahoo Finance
        figure = {
            'data': [
                go.Candlestick(
                    x=data['datetime'],
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name="OHLC"
                )
            ],
            'layout': go.Layout(
                title=f"{table.replace('_', ' ').title()} Data",
                xaxis={'title': 'Datetime'},
                yaxis={'title': 'Price'},
                template="plotly_dark"
            )
        }
    return figure

def run_dashboard_with_stream():
    """
    Launch the WebSocket streamer and the dashboard together.
    """
    print("🚀 Starting Alpaca real-time streamer in the background...")
    stream_thread = Thread(target=start_stream)
    stream_thread.daemon = True  # Daemon thread to stop when the main thread stops
    stream_thread.start()

    print("🚀 Launching the Ishara Trading Dashboard...")
    app.run_server(debug=True)

if __name__ == '__main__':
    run_dashboard_with_stream()
    