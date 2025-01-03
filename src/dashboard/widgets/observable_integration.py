import json
from dash_deck import DeckGL
import pandas as pd


class ObservableIntegration:
    """
    A utility class for creating and embedding Observable.js visualizations
    with dynamic data.
    """

    @staticmethod
    def preprocess_cluster_data(cluster_data):
        """
        Extracts 'x', 'y', and 'cluster' columns from the 'result' JSON field in the cluster_data DataFrame.

        Args:
            cluster_data (pd.DataFrame): The original DataFrame with a 'result' column.

        Returns:
            pd.DataFrame: A DataFrame with 'x', 'y', and 'cluster' columns extracted.
        """
        if "result" not in cluster_data:
            raise ValueError("Missing 'result' column in cluster data.")

        def extract_features(row):
            try:
                result = row["result"]
                x = result["features"]["low"]   # Replace with your desired x feature
                y = result["features"]["high"]  # Replace with your desired y feature
                cluster = row["cluster_id"]     # Assuming this maps directly to 'cluster'
                return pd.Series({"x": x, "y": y, "cluster": cluster})
            except KeyError as e:
                print(f"❌ Error extracting features: {e}")
                return pd.Series({"x": None, "y": None, "cluster": None})

        extracted = cluster_data.apply(extract_features, axis=1)
        return extracted.dropna()  # Drop rows with missing values

    @staticmethod
    def plot_trend_line_regression(cluster_data):
        """
        Generates a trend line regression visualization using Observable.js.

        Args:
            cluster_data (pd.DataFrame): A DataFrame with columns 'x', 'y', and 'cluster'.

        Returns:
            DeckGL: A DeckGL component embedding the Observable.js visualization.
        """
        if cluster_data.empty:
            raise ValueError("No clustering data available for visualization.")

        print(f"DEBUG: Cluster data: {cluster_data.head()}")

        # Ensure the necessary columns are present
        required_columns = {"x", "y", "cluster"}
        if not required_columns.issubset(cluster_data.columns):
            raise ValueError(f"Cluster data must contain columns: {required_columns}")

        # Convert DataFrame to JSON-like structure
        cluster_json = cluster_data[["x", "y", "cluster"]].to_dict(orient="records")

        # Observable.js script
        observable_script = """
        const Plot = require('https://cdn.jsdelivr.net/npm/@observablehq/plot');

        export default function render({data}) {
            const container = document.createElement('div');
            container.style.width = '100%';
            container.style.height = '100%';

            const chart = Plot.plot({
                marks: [
                    Plot.dot(data, {x: 'x', y: 'y', fill: 'cluster'}),
                    Plot.regression(data, {x: 'x', y: 'y', stroke: 'cluster'}),
                ],
                height: 500,
                marginLeft: 50,
                marginBottom: 50,
                grid: true,
            });

            container.appendChild(chart);
            return container;
        }
        """

        # Embed the Observable visualization using DeckGL
        return DeckGL(
            mapboxKey="",  # Optional if a background map is needed
            data=json.dumps({"data": cluster_json}),
            script=observable_script,
            style={"height": "600px", "width": "100%"},
        )
    