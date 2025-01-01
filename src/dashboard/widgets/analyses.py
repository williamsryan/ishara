from dash import dcc, html
from dash.exceptions import PreventUpdate
from src.processors.analysis import Analysis

class Analyses:
    def layout(self, symbols=None, start_date=None, end_date=None):
        """
        Render the layout for the analyses tab.
        """
        if not symbols:
            return html.Div("⚠️ Please select symbols to analyze.", className="text-warning p-3")

        # Dropdown for selecting analysis type
        analysis_dropdown = dcc.Dropdown(
            id="analysis-type-dropdown",
            options=[
                {"label": "K-NN Clustering", "value": "knn_clustering"},
                {"label": "Graph Clustering", "value": "graph_clustering"},
                {"label": "Regime Analysis", "value": "regime_analysis"},
            ],
            placeholder="Select analysis type",
            className="mb-3",
        )

        # Analysis status and content
        analysis_status = html.Div(id="analysis-status", className="text-muted mb-3")
        analysis_results = html.Div(id="analyses-tab-content", className="mt-4")

        # Return the layout
        return html.Div([
            html.H4("Run Analyses", className="mb-3"),
            analysis_dropdown,
            html.Button("Run Analysis", id="run-analysis", className="btn btn-primary mb-3"),
            analysis_status,
            analysis_results,
        ])
        