from dash import dcc, html
import plotly.graph_objs as go
from src.utils.database import connect_to_db
import pandas as pd

class PriceChart:
    def layout(self, symbols):
        try:
            conn = connect_to_db()
            query = f"SELECT datetime, close, symbol FROM historical_market_data WHERE symbol IN ({','.join([f'\'{s}\'' for s in symbols])})"
            data = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            return html.Div(f"❌ Error fetching price data: {e}")

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
        try:
            conn = connect_to_db()
            query = f"SELECT * FROM alternative_data WHERE symbol IN ({','.join([f'\'{s}\'' for s in symbols])})"
            data = pd.read_sql(query, conn)
            conn.close()
        except Exception as e:
            return html.Div(f"❌ Error fetching alternative data: {e}")

        if data.empty:
            return html.Div("⚠️ No alternative data available.")

        figures = []
        for metric in data["metric"].unique():
            metric_data = data[data["metric"] == metric]
            fig = go.Figure()
            for symbol in symbols:
                symbol_data = metric_data[metric_data["symbol"] == symbol]
                if metric == "mentions":
                    fig.add_trace(go.Bar(
                        x=symbol_data["datetime"], y=symbol_data["value"], name=f"{symbol} Mentions"
                    ))
                else:
                    fig.add_trace(go.Scatter(
                        x=symbol_data["datetime"], y=symbol_data["value"], mode="lines", name=f"{symbol} {metric.capitalize()}"
                    ))
            fig.update_layout(title=f"{metric.capitalize()} Over Time", template="plotly_white")
            figures.append(dcc.Graph(figure=fig))

        return html.Div(figures)
    