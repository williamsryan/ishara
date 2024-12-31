import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import plotly.graph_objects as go
import json
from src.utils.database import fetch_data, insert_clustering_results

class Analysis:
    def __init__(self):
        pass

    @staticmethod
    def fetch_clustering_results(cluster_type):
        """
        Fetch clustering results from the analysis_results table.
        """
        query = f"""
        SELECT symbol, cluster_id, result
        FROM analysis_results
        WHERE analysis_type = '{cluster_type}'
        """
        data = fetch_data(query)

        if data.empty:
            print(f"⚠️ No {cluster_type} clustering results found.")
            return pd.DataFrame()

        # Filter out rows with None or NULL in the result column
        data = data[data["result"].notnull()]

        if data.empty:
            print(f"⚠️ No valid {cluster_type} clustering results found.")
            return pd.DataFrame()
        
        print(f"TEST: {type(data['result'])}")
        
        # Parse JSON result column
        data["parsed_result"] = data["result"].apply(json.loads)
        return data

    @staticmethod
    def perform_knn_clustering(symbols, start_date, end_date):
        """
        Perform K-NN clustering for the given symbols.
        """
        query = f"""
        SELECT *
        FROM historical_market_data
        WHERE symbol IN ({','.join(f"'{s}'" for s in symbols)})
        AND datetime BETWEEN '{start_date}' AND '{end_date}'
        """
        data = fetch_data(query)

        if data.empty:
            raise ValueError("No data available for the given symbols and date range.")

        features = data.drop(columns=["datetime", "symbol"])
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        kmeans = KMeans(n_clusters=3, random_state=42)
        data["cluster_id"] = kmeans.fit_predict(features_normalized)

        # Prepare results for insertion
        clustering_results = []
        for _, row in data.iterrows():
            result_data = {
                "features": row[features.columns].to_dict(),
                "cluster_center": kmeans.cluster_centers_[int(row["cluster_id"])].tolist()
            }
            clustering_results.append((
                row["symbol"],
                "knn_clustering",
                row["cluster_id"],
                json.dumps(result_data)  # Serialize dict to JSON string
            ))

        insert_clustering_results(clustering_results)
        return data

    @staticmethod
    def perform_graph_clustering(symbols, start_date, end_date):
        """
        Perform graph-based clustering for the given symbols.
        """
        # Historical data query
        historical_query = f"""
        SELECT symbol, datetime, close, open
        FROM historical_market_data
        WHERE symbol IN ({','.join(f"'{s}'" for s in symbols)})
        AND datetime BETWEEN '{start_date}' AND '{end_date}'
        AND close IS NOT NULL AND open IS NOT NULL
        """
        historical_data = fetch_data(historical_query)

        if historical_data.empty:
            raise ValueError("No historical data available for clustering analysis.")

        # Fetch and process options data
        options_query = f"""
        SELECT symbol, implied_volatility, open_interest, strike
        FROM options_data
        WHERE symbol IN ({','.join(f"'{s}'" for s in symbols)})
        AND implied_volatility IS NOT NULL AND open_interest IS NOT NULL
        """
        options_data = fetch_data(options_query)

        if options_data.empty:
            raise ValueError("No options data available for clustering analysis.")

        # Derived metrics
        historical_data["log_returns"] = np.log(historical_data["close"] / historical_data["open"])
        historical_features = historical_data.groupby("symbol").agg({"log_returns": "mean"}).reset_index()

        options_features = options_data.groupby("symbol").agg({
            "implied_volatility": "mean",
            "open_interest": "sum",
            "strike": "mean"
        }).reset_index()

        derived_data = pd.merge(historical_features, options_features, on="symbol", how="inner")

        # Normalize features
        features = ["log_returns", "implied_volatility", "open_interest", "strike"]
        scaler = StandardScaler()
        normalized_data = scaler.fit_transform(derived_data[features])

        # Build graph
        similarity_matrix = cosine_similarity(normalized_data)
        graph = nx.Graph()
        threshold = 0.8
        for i in range(len(derived_data)):
            for j in range(i + 1, len(derived_data)):
                if similarity_matrix[i, j] > threshold:
                    graph.add_edge(derived_data.iloc[i]["symbol"], derived_data.iloc[j]["symbol"])

        centrality = nx.degree_centrality(graph)
        clustering_coefficient = nx.clustering(graph)

        # Clusters and results
        clusters = list(nx.connected_components(graph))
        graph_clustering_results = []
        for cluster_id, cluster in enumerate(clusters):
            for symbol in cluster:
                result_data = {
                    "connected_symbols": list(cluster),
                    "centrality": centrality[symbol],
                    "clustering_coefficient": clustering_coefficient[symbol],
                    "symbol_metrics": derived_data[derived_data["symbol"] == symbol][features].to_dict(orient="records")[0],
                }
                graph_clustering_results.append((
                    symbol,
                    "graph_clustering",
                    cluster_id,
                    json.dumps(result_data)  # Serialize the dict to JSON
                ))

        insert_clustering_results(graph_clustering_results)

        return graph, clusters

    @staticmethod
    def plot_graph_clusters(results):
        """
        Visualize graph-based clusters using NetworkX and Plotly.
        """
        graph = nx.Graph()
        
        # Parse the JSON data in the result column to build the graph
        for _, row in results.iterrows():
            result_data = json.loads(row["result"])
            connected_symbols = result_data.get("connected_symbols", [])
            for symbol in connected_symbols:
                graph.add_edge(row["symbol"], symbol)

        # Assign cluster colors based on cluster_id
        cluster_ids = {row["symbol"]: row["cluster_id"] for _, row in results.iterrows()}
        color_map = [cluster_ids[node] for node in graph]

        # Plot the graph
        pos = nx.spring_layout(graph)  # Generate layout
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
        results["parsed_result"] = results["result"].apply(json.loads)
        results["x"] = results["parsed_result"].apply(lambda d: d["features"].get(features[0]))
        results["y"] = results["parsed_result"].apply(lambda d: d["features"].get(features[1]))

        # Create a scatter plot with clusters
        fig = go.Figure()
        for cluster_id, cluster_data in results.groupby("cluster_id"):
            fig.add_trace(
                go.Scatter(
                    x=cluster_data["x"],
                    y=cluster_data["y"],
                    mode="markers",
                    name=f"Cluster {cluster_id}",
                    marker=dict(size=10)
                )
            )

        fig.update_layout(
            title="Cluster Scatter Plot",
            xaxis_title=features[0],
            yaxis_title=features[1],
            template="plotly_white"
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
    