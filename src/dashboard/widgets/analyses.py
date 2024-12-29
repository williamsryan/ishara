from dash import html, dcc
import plotly.graph_objs as go
from src.dashboard.widgets.chart_components import KnnClusteringChart, GraphClusteringChart

class Analyses:
    def layout(self, symbols=None, start_date=None, end_date=None):
        """
        Renders the layout for the Analyses tab.
        
        Args:
            symbols (list): List of symbols to analyze.
            start_date (str): Start date for the analysis range.
            end_date (str): End date for the analysis range.

        Returns:
            dash.html.Div: Layout for the Analyses tab.
        """
        knn_chart = KnnClusteringChart()
        graph_chart = GraphClusteringChart()

        # Handle missing symbols, start_date, or end_date
        if not symbols:
            return html.Div("⚠️ Please select symbols to display analysis.", className="text-warning p-3")

        if not start_date or not end_date:
            return html.Div("⚠️ Please select a valid date range for analysis.", className="text-warning p-3")

        # Build the layout
        return html.Div([
            html.H4("Run Clustering Analyses", className="mb-4"),
            dcc.Loading(type="circle", children=[
                html.Div(id="analysis-status", className="text-info mb-3"),
                html.Button("Run Analyses", id="run-analysis", className="btn btn-primary mb-4"),
            ]),
            html.Div("K-NN Clustering Results", className="font-weight-bold mt-3"),
            knn_chart.layout(symbols, start_date, end_date),
            html.Div("Graph-Based Clustering Results", className="font-weight-bold mt-5"),
            graph_chart.layout(symbols, start_date, end_date),
        ])
    