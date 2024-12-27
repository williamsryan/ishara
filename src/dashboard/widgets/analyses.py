from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
from src.utils.database import connect_to_db

class Analyses:
    def layout(self, symbols, start_date, end_date):
        return html.Div([
            html.H4("Clustering Analysis"),
            dcc.Graph(id="clustering-result"),
            html.H4("Regime Analysis"),
            dcc.Graph(id="regime-result"),
            html.Button("Run Analyses", id="run-analyses", className="btn btn-primary mt-3")
        ])

    def run_clustering_analysis(self, symbols):
        # Example clustering logic, replace with actual implementation
        conn = connect_to_db()
        query = f"""
            SELECT feature1, feature2, cluster, symbol
            FROM clustering_results
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return go.Figure().update_layout(title="No Clustering Results Available")

        fig = go.Figure()
        for cluster_id in data["cluster"].unique():
            cluster_data = data[data["cluster"] == cluster_id]
            fig.add_trace(go.Scatter(
                x=cluster_data["feature1"], y=cluster_data["feature2"],
                mode="markers", name=f"Cluster {cluster_id}",
                marker=dict(size=10)
            ))

        fig.update_layout(title="Clustering Results", xaxis_title="Feature 1", yaxis_title="Feature 2")
        return fig

    def run_regime_analysis(self, symbols):
        # Example regime logic, replace with actual implementation
        conn = connect_to_db()
        query = f"""
            SELECT datetime, regime, value, symbol
            FROM regime_analysis
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return go.Figure().update_layout(title="No Regime Analysis Results Available")

        fig = go.Figure()
        for regime_id in data["regime"].unique():
            regime_data = data[data["regime"] == regime_id]
            fig.add_trace(go.Scatter(
                x=regime_data["datetime"], y=regime_data["value"],
                mode="lines", name=f"Regime {regime_id}"
            ))

        fig.update_layout(title="Regime Analysis Results", xaxis_title="Datetime", yaxis_title="Metric Value")
        return fig
    