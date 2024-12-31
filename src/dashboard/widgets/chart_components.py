from dash import dcc, html
import plotly.graph_objs as go
import networkx as nx
from src.utils.database import fetch_data
import pandas as pd

class PriceChart:
    def layout(self, symbols, start_date, end_date, data_source):
        # Build the query dynamically based on the selected data source
        query = f"""
            SELECT datetime, close, symbol
            FROM {data_source} 
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
            ORDER BY datetime ASC
        """
        # params = tuple(symbols) + (start_date, end_date)
        results = fetch_data(query, params=tuple(symbols,))

        # Check if the DataFrame is empty
        if results.empty:
            return html.Div("⚠️ No price data available for the selected criteria.", className="text-warning p-3")

        figure = go.Figure()
        for symbol in symbols:
            symbol_data = results[results["symbol"] == symbol]
            figure.add_trace(go.Scatter(
                x=symbol_data["datetime"], y=symbol_data["close"], mode="lines", name=f"{symbol} Price"
            ))

        figure.update_layout(title="Price Chart", xaxis_title="Datetime", yaxis_title="Close Price")
        return dcc.Graph(figure=figure)

class AlternativeDataCharts:
    def layout(self, symbols):
        if not symbols:
            return html.Div("⚠️ Please select symbols to display data.", className="text-warning p-3")

        query = f"""
            SELECT DISTINCT metric
            FROM alternative_data
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
        """
        params = tuple(symbols)
        results = fetch_data(query, params=params)

        if results.empty:
            return html.Div("⚠️ No alternative data available for the selected symbols.", className="text-warning p-3")

        metrics = results["metric"].unique()
        metric_options = [{"label": metric.capitalize(), "value": metric} for metric in metrics]

        return html.Div([
            html.Label("Select Metrics to Display"),
            dcc.Checklist(
                id="metric-filter",
                options=metric_options,
                value=metrics.tolist(),  # Default to all metrics
                inline=True,
                className="mb-4"
            ),
            html.Div(id="alternative-data-graphs"),
        ])

    def render_graphs(self, symbols, selected_metrics):
        if not symbols or not selected_metrics:
            return html.Div("⚠️ Please select symbols and metrics to display data.", className="text-warning p-3")

        query = f"""
            SELECT datetime, metric, value, symbol
            FROM alternative_data
            WHERE symbol IN ({','.join(['%s'] * len(symbols))}) AND metric = ANY(%s)
        """
        params = tuple(symbols) + (selected_metrics,)
        results = fetch_data(query, params=params)

        if results.empty:
            return html.Div("⚠️ No data available for the selected metrics.", className="text-warning p-3")

        graphs = []
        for metric in selected_metrics:
            metric_data = results[results["metric"] == metric]
            fig = go.Figure()
            for symbol in symbols:
                symbol_data = metric_data[metric_data["symbol"] == symbol]
                fig.add_trace(go.Scatter(
                    x=symbol_data["datetime"], y=symbol_data["value"],
                    mode="lines", name=f"{symbol} {metric}"
                ))
            fig.update_layout(
                title=f"{metric.capitalize()} Over Time",
                xaxis_title="Datetime",
                yaxis_title="Value"
            )
            graphs.append(dcc.Graph(figure=fig))

        return html.Div(graphs)
    