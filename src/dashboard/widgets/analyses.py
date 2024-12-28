from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
from src.dashboard.widgets.chart_components import KnnClusteringChart, GraphClusteringChart

class Analyses:
    def layout(self, symbols, start_date, end_date):
        knn_chart = KnnClusteringChart()
        graph_chart = GraphClusteringChart()

        return html.Div([
            html.H4("Run Clustering Analyses"),
            dcc.Loading(type="circle", children=[
                html.Div(id="analysis-status", className="text-info mb-3"),
                html.Button("Run Analyses", id="run-analysis", className="btn btn-primary"),
            ]),
            knn_chart.layout(),
            graph_chart.layout(),
        ])
    