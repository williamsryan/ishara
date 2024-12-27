from dash import dcc, html
import plotly.graph_objs as go
from src.utils.database import connect_to_db
import pandas as pd

class PriceChart:
    def layout(self, symbols, start_date, end_date):
        conn = connect_to_db()
        query = f"""
            SELECT datetime, close, symbol
            FROM historical_market_data
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
              AND datetime BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY datetime ASC
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return html.Div("⚠️ No price data available for the selected criteria.")

        figure = go.Figure()
        for symbol in symbols:
            symbol_data = data[data["symbol"] == symbol]
            figure.add_trace(go.Scatter(x=symbol_data["datetime"], y=symbol_data["close"],
                                        mode="lines", name=f"{symbol} Price"))

        figure.update_layout(title="Price Chart", template="plotly_white")
        return dcc.Graph(figure=figure)

class AlternativeDataCharts:
    def layout(self, symbols, start_date, end_date, overlay_toggle):
        conn = connect_to_db()
        query = f"""
            SELECT datetime, value, metric, symbol
            FROM alternative_data
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
              AND datetime BETWEEN '{start_date}' AND '{end_date}'
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return html.Div("⚠️ No alternative data available.")

        figures = []
        for metric in data["metric"].unique():
            metric_data = data[data["metric"] == metric]
            fig = go.Figure()
            for symbol in symbols:
                symbol_data = metric_data[metric_data["symbol"] == symbol]
                fig.add_trace(go.Scatter(x=symbol_data["datetime"], y=symbol_data["value"],
                                         mode="lines", name=f"{symbol} {metric}"))

            fig.update_layout(title=f"{metric.capitalize()} Over Time", template="plotly_white")
            figures.append(dcc.Graph(figure=fig))

        return html.Div(figures)
    