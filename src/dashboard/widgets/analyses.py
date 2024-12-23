from dash import dcc, html
import plotly.graph_objs as go
from src.processors.clustering_analysis import perform_clustering_analysis
from src.processors.regime_analysis import perform_regime_analysis

class AnalysisCharts:
    def layout(self, symbols):
        clustering_fig = perform_clustering_analysis(symbols)
        regime_fig = perform_regime_analysis(symbols)

        return html.Div([
            dcc.Graph(figure=clustering_fig, id="clustering-chart"),
            dcc.Graph(figure=regime_fig, id="regime-chart")
        ])