from dash import dcc, html
import plotly.graph_objs as go
from src.utils.database import connect_to_db
import pandas as pd

class PriceChart:
    def layout(self, symbols):
        conn = connect_to_db()
        query = f"SELECT datetime, close FROM historical_market_data WHERE symbol IN ({','.join([f'\'{s}\'' for s in symbols])})"
        data = pd.read_sql(query, conn)
        conn.close()

        if data.empty:
            return html.Div("⚠️ No price data available.")
        
        figure = go.Figure()
        for symbol in symbols:
            symbol_data = data[data["symbol"] == symbol]
            figure.add_trace(go.Scatter(x=symbol_data["datetime"], y=symbol_data["close"],
                                        mode="lines", name=f"{symbol} Price"))

        figure.update_layout(title="Price Chart", template="plotly_white")
        return dcc.Graph(figure=figure)

class AlternativeDataCharts:
    def layout(self, symbols):
        conn = connect_to_db()
        query = f"SELECT * FROM alternative_data WHERE symbol IN ({','.join([f'\'{s}\'' for s in symbols])})"
        data = pd.read_sql(query, conn)
        conn.close()

        if data.empty:
            return html.Div("⚠️ No alternative data available.")

        sentiment_data = data[data["metric"] == "sentiment_score"]
        mentions_data = data[data["metric"] == "mentions"]

        sentiment_fig = go.Figure()
        mentions_fig = go.Figure()

        for symbol in symbols:
            symbol_sentiment = sentiment_data[sentiment_data["symbol"] == symbol]
            sentiment_fig.add_trace(go.Scatter(
                x=symbol_sentiment["datetime"], y=symbol_sentiment["value"],
                mode="lines", name=f"{symbol} Sentiment"
            ))

            symbol_mentions = mentions_data[mentions_data["symbol"] == symbol]
            mentions_fig.add_trace(go.Bar(
                x=symbol_mentions["datetime"], y=symbol_mentions["value"],
                name=f"{symbol} Mentions"
            ))

        return html.Div([
            dcc.Graph(figure=sentiment_fig),
            dcc.Graph(figure=mentions_fig)
        ])
    