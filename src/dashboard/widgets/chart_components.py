from dash import dcc, html
import plotly.graph_objs as go
import networkx as nx
from src.utils.database import fetch_data
import pandas as pd

class PriceChart:
    @staticmethod
    def layout(symbols, data_source, start_date=None, end_date=None, selected_indicators=None):
        """
        Generate the layout for the price chart with an indicator dropdown.

        Args:
            symbols (list): List of symbols to fetch data for.
            start_date (str, optional): Start date for the query range.
            end_date (str, optional): End date for the query range.
            selected_indicators (list, optional): List of selected indicators.

        Returns:
            html.Div: Layout including price chart and indicator dropdown.
        """
        if not symbols:
            return html.Div("⚠️ No symbols selected. Please select symbols to display data.", className="text-warning p-3")

        query = f"""
            SELECT datetime, close, open, high, low, volume, symbol
            FROM {data_source}
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
        """
        params = list(symbols)
        if start_date and end_date:
            query += " AND datetime BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        query += " ORDER BY datetime ASC"

        results = fetch_data(query, tuple(params))
        if results.empty:
            return html.Div("⚠️ No data available for the selected criteria.", className="text-warning p-3")

        # Create dropdown for selecting indicators
        indicator_dropdown = dcc.Dropdown(
            id="indicator-selector",
            options=[
                {"label": "Moving Average (MA)", "value": "ma"},
                {"label": "Bollinger Bands (BB)", "value": "bb"}
            ],
            multi=True,
            placeholder="Select Indicators",
            value=selected_indicators if selected_indicators else [],
            className="mb-3"
        )

        # Create chart figure
        fig = go.Figure()

        for symbol in symbols:
            symbol_data = results[results["symbol"] == symbol]
            fig.add_trace(go.Scatter(
                x=symbol_data["datetime"], y=symbol_data["close"], mode="lines", name=f"{symbol} Close"
            ))

            # Add indicators if selected
            if selected_indicators:
                if "ma" in selected_indicators:
                    symbol_data["ma"] = symbol_data["close"].rolling(window=20).mean()
                    fig.add_trace(go.Scatter(
                        x=symbol_data["datetime"], y=symbol_data["ma"], mode="lines", name=f"{symbol} MA (20)"
                    ))
                if "bb" in selected_indicators:
                    rolling_mean = symbol_data["close"].rolling(window=20).mean()
                    rolling_std = symbol_data["close"].rolling(window=20).std()
                    symbol_data["bb_upper"] = rolling_mean + (rolling_std * 2)
                    symbol_data["bb_lower"] = rolling_mean - (rolling_std * 2)

                    # Add Bollinger Bands with fill
                    fig.add_trace(go.Scatter(
                        x=symbol_data["datetime"],
                        y=symbol_data["bb_upper"],
                        mode="lines",
                        name=f"{symbol} BB Upper",
                        line=dict(color='rgba(173, 216, 230, 0.6)')  # Light blue
                    ))
                    fig.add_trace(go.Scatter(
                        x=symbol_data["datetime"],
                        y=symbol_data["bb_lower"],
                        mode="lines",
                        name=f"{symbol} BB Lower",
                        line=dict(color='rgba(173, 216, 230, 0.6)'),  # Light blue
                        fill='tonexty',  # Fill to the previous trace
                        fillcolor='rgba(173, 216, 230, 0.2)'  # Light blue fill
                    ))

        fig.update_layout(
            # title="Price Chart with Indicators",
            xaxis_title="Datetime",
            yaxis_title="Price",
            template="plotly_white",
            height=600,
            dragmode="zoom",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return html.Div([
            html.Div([indicator_dropdown], className="mb-3"),
            dcc.Graph(figure=fig, id="price-chart")
        ])

class AlternativeDataCharts:
    @staticmethod
    def layout(symbols):
        """
        Layout for alternative data charts.
        """
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

    @staticmethod
    def render_graphs(symbols, selected_metrics):
        """
        Render alternative data graphs with enhancements.

        Args:
            symbols (list): List of selected symbols.
            selected_metrics (list): List of selected metrics.

        Returns:
            html.Div: Div containing rendered graphs.
        """
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

                # Add cumulative plot for mentions
                if metric == "mentions":
                    symbol_data["cumulative"] = symbol_data["value"].cumsum()
                    fig.add_trace(go.Scatter(
                        x=symbol_data["datetime"], y=symbol_data["cumulative"],
                        mode="lines", name=f"{symbol} Cumulative Mentions", line=dict(dash="dot")
                    ))

            fig.update_layout(
                title=f"{metric.capitalize()} Over Time",
                xaxis_title="Datetime",
                yaxis_title="Value",
                template="plotly_white",
                height=400,
                dragmode="pan"
            )
            graphs.append(dcc.Graph(figure=fig))

        return html.Div(graphs)
    