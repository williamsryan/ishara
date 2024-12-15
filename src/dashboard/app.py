from dash import Dash, dcc, html
import pandas as pd
import plotly.graph_objs as go

app = Dash(__name__)
data = pd.read_csv("data/raw/aapl_historical.csv")

app.layout = html.Div([
    html.H1("Ishara Dashboard"),
    dcc.Graph(
        id="price-chart",
        figure={
            "data": [
                go.Candlestick(
                    x=data['timestamp'],
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name="Price"
                )
            ],
            "layout": {"title": "AAPL Historical Prices"}
        }
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
    