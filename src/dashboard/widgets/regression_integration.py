from dash import html, dcc
import plotly.graph_objects as go
import numpy as np
import pandas as pd

class RegressionInterface:
    """
    A utility class for creating visualizations with cluster data.
    """

    @staticmethod
    def preprocess_cluster_data(cluster_data):
        """
        Prepares the cluster data for visualization.

        Args:
            cluster_data (pd.DataFrame): Raw cluster data.

        Returns:
            pd.DataFrame: DataFrame with 'x', 'y', 'cluster', and additional metadata.
        """
        if "result" not in cluster_data:
            raise ValueError("Missing 'result' column in cluster data.")

        def extract_features(row):
            try:
                result = row["result"]
                x = result["features"]["low"]   # Replace with desired x feature
                y = result["features"]["high"]  # Replace with desired y feature
                cluster = row["cluster_id"]
                symbol = row["symbol"]          # Assuming the cluster data includes a 'symbol' column
                return {"x": x, "y": y, "cluster": cluster, "symbol": symbol}
            except KeyError as e:
                print(f"❌ Error extracting features: {e}")
                return None

        extracted = cluster_data.apply(extract_features, axis=1)
        return pd.DataFrame([e for e in extracted if e is not None])

    @staticmethod
    def plot_trend_line_regression(cluster_data):
        """
        Generates a trend line regression visualization with improved hover information.

        Args:
            cluster_data (pd.DataFrame): Preprocessed cluster data.

        Returns:
            html.Div: A Dash component containing the Plotly figure.
        """
        if cluster_data.empty:
            raise ValueError("No clustering data available for visualization.")

        fig = go.Figure()

        # Add scatter plot and regression line for each cluster
        for cluster_id, cluster_points in cluster_data.groupby("cluster"):
            # Scatter plot for cluster points with hover info
            fig.add_trace(
                go.Scatter(
                    x=cluster_points["x"],
                    y=cluster_points["y"],
                    mode="markers",
                    name=f"Cluster {cluster_id}",
                    marker=dict(size=6, opacity=0.7, line=dict(width=1)),
                    hovertemplate=(
                        "<b>Symbol:</b> %{customdata[0]}<br>"
                        "<b>Cluster:</b> %{customdata[1]}<br>"
                        "<b>X:</b> %{x}<br>"
                        "<b>Y:</b> %{y}<extra></extra>"
                    ),
                    customdata=cluster_points[["symbol", "cluster"]].values,
                )
            )

            # Linear regression
            x = cluster_points["x"].values
            y = cluster_points["y"].values
            if len(x) > 1:
                coef = np.polyfit(x, y, 1)  # Linear regression coefficients
                reg_line = coef[0] * x + coef[1]
                # Calculate residuals for error bands
                residuals = y - reg_line
                std_error = np.std(residuals)

                # Add regression line
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=reg_line,
                        mode="lines",
                        name=f"Trend Line (Cluster {cluster_id})",
                        line=dict(color="red", dash="dot", width=2),
                    )
                )

                # Add error bands
                fig.add_trace(
                    go.Scatter(
                        x=np.concatenate([x, x[::-1]]),
                        y=np.concatenate([reg_line + std_error, (reg_line - std_error)[::-1]]),
                        fill="toself",
                        fillcolor="rgba(255, 0, 0, 0.2)",
                        line=dict(color="rgba(255, 0, 0, 0)"),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

        # Update layout for better aesthetics
        fig.update_layout(
            title="Cluster Trend Lines with Detailed Hover Info",
            xaxis_title="Low",
            yaxis_title="High",
            height=600,
            template="plotly_white",
            showlegend=True,
            margin=dict(l=40, r=40, t=40, b=40),
            font=dict(size=12),
        )

        return html.Div(dcc.Graph(figure=fig), style={"width": "100%"})
    