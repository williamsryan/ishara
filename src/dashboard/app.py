import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from src.utils.database import connect_to_db

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Ishara Trading Dashboard"

def fetch_data(table):
    """
    Fetch data from the specified database table.
    """
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
        value='real_time_market_data',
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
    data = fetch_data(table)
    if data.empty:
        return {"layout": {"title": "No Data Available"}}

    if "close" in data.columns:
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
            'layout': go.Layout(title=f"{table} Data", xaxis={'title': 'Datetime'}, yaxis={'title': 'Price'})
        }
    else:
        figure = {
            'data': [
                go.Scatter(
                    x=data['datetime'],
                    y=data['value'],
                    mode='lines+markers',
                    name="Metric Value"
                )
            ],
            'layout': go.Layout(title="Alternative Data Trends", xaxis={'title': 'Datetime'}, yaxis={'title': 'Value'})
        }
    return figure

def run_dashboard():
    app.run_server(debug=True)

if __name__ == '__main__':
    run_dashboard()
    