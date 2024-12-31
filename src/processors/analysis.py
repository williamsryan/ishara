import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import plotly.graph_objects as go
# import plotly.express as px
import json
from src.utils.database import fetch_as_dataframe, insert_clustering_results

class Analysis:
    def __init__(self):
        pass

    @staticmethod
    def fetch_clustering_results(cluster_type):
        """
        Fetch clustering results from the analysis_results table.
        """
        query = f"""
        SELECT symbol, cluster_id, details
        FROM analysis_results
        WHERE analysis_type = '{cluster_type}'
        """
        data = fetch_as_dataframe(query)
        if data.empty:
            print(f"⚠️ No {cluster_type} clustering results found.")
            return pd.DataFrame()

        # Parse JSON details column
        data["details"] = data["details"].apply(json.loads)
        return data

    @staticmethod
    def perform_knn_clustering(symbols, start_date, end_date):
        """
        Perform K-NN clustering on the given data.
        """
        query = f"""
        SELECT *
        FROM market_data
        WHERE symbol IN ({','.join(f"'{s}'" for s in symbols)})
          AND datetime BETWEEN '{start_date}' AND '{end_date}'
        """
        data = fetch_as_dataframe(query)

        if data.empty:
            raise ValueError("No data available for the given symbols and date range.")

        features = data.drop(columns=["datetime", "symbol"])
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        kmeans = KMeans(n_clusters=3, random_state=42)
        data["cluster_id"] = kmeans.fit_predict(features_normalized)

        # Store cluster centroids
        centroids = kmeans.cluster_centers_
        for idx, centroid in enumerate(centroids):
            insert_clustering_results("knn", f"Cluster {idx}", json.dumps({"centroid": centroid.tolist()}))

        return data

    @staticmethod
    def perform_graph_clustering(symbols, start_date, end_date):
        """
        Perform graph-based clustering on the given data.
        """
        query = f"""
        SELECT *
        FROM market_data
        WHERE symbol IN ({','.join(f"'{s}'" for s in symbols)})
          AND datetime BETWEEN '{start_date}' AND '{end_date}'
        """
        data = fetch_as_dataframe(query)

        if data.empty:
            raise ValueError("No data available for the given symbols and date range.")

        similarity_matrix = cosine_similarity(data.drop(columns=["datetime", "symbol"]))
        graph = nx.Graph()
        for i, row_symbol in enumerate(data["symbol"]):
            for j, col_symbol in enumerate(data["symbol"]):
                if i != j and similarity_matrix[i, j] > 0.8:
                    graph.add_edge(row_symbol, col_symbol)

        communities = list(greedy_modularity_communities(graph))
        return graph, communities

    @staticmethod
    def plot_graph_clusters(results):
        """
        Visualize graph-based clusters using NetworkX and Plotly.
        """
        graph = nx.Graph()
        for _, row in results.iterrows():
            connected_symbols = row["details"]["connected_symbols"]
            for symbol in connected_symbols:
                graph.add_edge(row["symbol"], symbol)

        # Assign cluster colors
        cluster_ids = {row["symbol"]: row["cluster_id"] for _, row in results.iterrows()}
        color_map = [cluster_ids[node] for node in graph]

        # Plot graph
        pos = nx.spring_layout(graph)
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace["x"] += [x0, x1, None]
            edge_trace["y"] += [y0, y1, None]

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                showscale=True,
                colorscale="YlGnBu",
                size=10,
                color=color_map,
                line_width=2,
            ),
        )

        for node in graph:
            x, y = pos[node]
            node_trace["x"] += [x]
            node_trace["y"] += [y]
            node_trace["text"] += [node]

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Graph-Based Clustering",
                showlegend=False,
                hovermode="closest",
                margin=dict(b=0, l=0, r=0, t=0),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False),
            ),
        )
        return fig

    @staticmethod
    def plot_cluster_scatter(results, features):
        """
        Plot 2D scatter plot of clustered data using normalized features.
        """
        data = pd.DataFrame(results)
        data["x"] = data["details"].apply(lambda d: d[features[0]])
        data["y"] = data["details"].apply(lambda d: d[features[1]])

        fig = go.scatter(
            data,
            x="x",
            y="y",
            color="cluster_id",
            title="Cluster Scatter Plot",
            labels={"x": features[0], "y": features[1]},
        )
        return fig

    @staticmethod
    def plot_community_summary(results):
        """
        Plot community sizes as a bar chart.
        """
        communities = results.groupby("cluster_id").size().reset_index(name="count")
        fig = go.bar(
            communities,
            x="cluster_id",
            y="count",
            title="Community Size Summary",
            labels={"cluster_id": "Community ID", "count": "Number of Symbols"},
        )
        return fig
    