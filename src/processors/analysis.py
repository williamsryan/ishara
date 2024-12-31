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
    def fetch_clustering_results(analysis_type, selected_symbols=None):
        """
        Fetch clustering results for a specific analysis type.
        Optionally filter by the selected symbols.
        """
        query = f"""
        SELECT *
        FROM analysis_results
        WHERE analysis_type = '{analysis_type}'
        """
        if selected_symbols:
            query += f" AND input_symbols @> '{json.dumps(selected_symbols)}'"

        results = fetch_data(query)
        if results.empty:
            print(f"⚠️ No results found for analysis type: {analysis_type} and symbols: {selected_symbols}")
        return results

    @staticmethod
    def perform_knn_clustering(selected_symbols, start_date, end_date):
        """
        Perform K-NN clustering for the selected symbols within a date range.
        """
        if not selected_symbols:
            raise ValueError("No symbols selected for clustering.")

        # Query the historical market data for the selected symbols
        symbols_filter = ", ".join(f"'{symbol}'" for symbol in selected_symbols)
        query = f"""
        SELECT *
        FROM historical_market_data
        WHERE symbol IN ({symbols_filter})
        """
        data = fetch_data(query)

        # Debugging: Check data size and preview
        print(f"DEBUG: Retrieved {len(data)} rows for symbols: {selected_symbols}")
        if data.empty:
            raise ValueError("No data available for the given symbols and date range.")

        # Aggregate data to one row per symbol (if needed)
        data = data.groupby("symbol").agg({
            "open": "mean",
            "high": "mean",
            "low": "mean",
            "close": "mean",
            "volume": "sum"
        }).reset_index()

        features = data.drop(columns=["symbol"])
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

        # Debugging: Check number of records to insert
        print(f"DEBUG: Prepared {len(clustering_results)} clustering results for insertion.")

        insert_clustering_results(clustering_results)
        print(f"✅ Stored K-NN clustering results for {len(data)} rows.")
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
        WHERE close IS NOT NULL AND open IS NOT NULL
        """
        historical_data = fetch_data(historical_query)

        if historical_data.empty:
            raise ValueError("No historical data available for clustering analysis.")

        # Fetch and process options data
        options_query = f"""
        SELECT symbol, implied_volatility, open_interest, strike
        FROM options_data
        WHERE implied_volatility IS NOT NULL AND open_interest IS NOT NULL
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

        if graph_clustering_results:
            insert_clustering_results(graph_clustering_results)
            print(f"✅ Stored graph clustering results for {len(clusters)} clusters.")
        else:
            print("⚠️ No graph clustering results to store.")

        return graph, clusters

    @staticmethod
    def plot_graph_clusters(results):
        """
        Visualize graph-based clusters using NetworkX and Plotly with improved interactivity and layout.
        """
        graph = nx.Graph()

        # Build the graph using data from the 'result' column
        for _, row in results.iterrows():
            result_data = row["result"]  # Assume this is already a dictionary
            connected_symbols = result_data.get("connected_symbols", [])
            for symbol in connected_symbols:
                graph.add_edge(row["symbol"], symbol)

        # Assign cluster colors based on cluster_id
        cluster_ids = {row["symbol"]: row["cluster_id"] for _, row in results.iterrows()}
        color_map = [cluster_ids.get(node, 0) for node in graph.nodes()]

        # Generate graph layout
        pos = nx.spring_layout(graph)

        # Initialize edge trace
        edge_x = []
        edge_y = []

        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        # Initialize node trace
        node_x = []
        node_y = []
        node_text = []

        for node in graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}<br>Cluster ID: {cluster_ids.get(node, 'N/A')}")

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            mode="markers",
            hoverinfo="text",
            marker=dict(
                showscale=True,
                colorscale="YlGnBu",
                size=15,
                color=color_map,
                line=dict(width=1, color="black"),
            ),
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Graph-Based Clustering",
                title_x=0.5,
                showlegend=False,
                hovermode="closest",
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )

        # Enable panning and zooming
        fig.update_layout(dragmode="pan")
        return fig

    @staticmethod
    def plot_cluster_scatter(results, features):
        """
        Plot 2D scatter plot of clustered data using normalized features.
        """
        # Ensure 'result' is properly parsed as JSON if not already
        if isinstance(results["result"].iloc[0], str):
            results["result"] = results["result"].apply(json.loads)

        # Extract x and y features from the JSON data
        results["x"] = results["result"].apply(lambda d: d.get("features", {}).get(features[0]))
        results["y"] = results["result"].apply(lambda d: d.get("features", {}).get(features[1]))
        results["volume"] = results["result"].apply(lambda d: d.get("features", {}).get("volume"))

        # Debugging: Check extracted data
        # print(f"DEBUG: Extracted x, y, and volume columns:\n{results[['x', 'y', 'volume']].head()}")

        # Filter out rows with None or invalid values in x or y
        results["x"] = pd.to_numeric(results["x"], errors="coerce")
        results["y"] = pd.to_numeric(results["y"], errors="coerce")
        filtered_results = results.dropna(subset=["x", "y"])
        if filtered_results.empty:
            print("⚠️ No valid data to plot for KNN clustering.")
            return go.Figure(
                layout=go.Layout(
                    title="KNN Cluster Scatter Plot",
                    xaxis_title=features[0],
                    yaxis_title=features[1],
                    template="plotly_white",
                    annotations=[
                        dict(
                            text="No valid data available for plotting",
                            xref="paper",
                            yref="paper",
                            showarrow=False,
                            font=dict(size=16),
                        )
                    ],
                )
            )

        # Create scatter plot
        fig = go.Figure()
        for cluster_id, cluster_data in filtered_results.groupby("cluster_id"):
            fig.add_trace(
                go.Scattergl(
                    x=cluster_data["x"],
                    y=cluster_data["y"],
                    mode="markers",
                    name=f"Cluster {cluster_id}",
                    marker=dict(
                        size=cluster_data["volume"] / cluster_data["volume"].max() * 20,  # Scale by volume
                        opacity=0.7,
                        line=dict(width=0.5, color="black"),
                    ),
                    text=[
                        f"Symbol: {symbol}<br>Low: {x}<br>High: {y}<br>Volume: {volume}"
                        for symbol, x, y, volume in zip(
                            cluster_data["symbol"], cluster_data["x"], cluster_data["y"], cluster_data["volume"]
                        )
                    ],
                    hoverinfo="text",
                )
            )

        # Add cluster center annotations
        for cluster_id, center in filtered_results.groupby("cluster_id")[["x", "y"]].mean().iterrows():
            fig.add_trace(go.Scatter(
                x=[center["x"]], y=[center["y"]],
                mode="markers+text",
                text=[f"Cluster {cluster_id}"],
                textposition="top center",
                marker=dict(size=15, color="black", symbol="x"),
                name=f"Cluster {cluster_id} Center"
            ))

        fig.update_layout(
            title="KNN Cluster Scatter Plot",
            title_x=0.5,
            xaxis_title=features[0],
            yaxis_title=features[1],
            template="plotly_white",
            dragmode="pan",  # Enable panning
            margin=dict(l=40, r=40, b=40, t=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )
        return fig

    @staticmethod
    def plot_community_summary(results):
        """
        Plot community sizes as a bar chart.
        """
        # Count the number of symbols in each cluster
        communities = results.groupby("cluster_id").size().reset_index(name="count")

        fig = go.Figure(
            data=[
                go.Bar(
                    x=communities["cluster_id"],
                    y=communities["count"],
                    text=communities["count"],
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title="Community Size Summary",
            xaxis_title="Community ID",
            yaxis_title="Number of Symbols",
            template="plotly_white",
        )
        return fig
    