import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import plotly.graph_objects as go
import json
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
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
    def perform_knn_clustering(selected_symbols, start_date, end_date, selected_features, reduction_method="none"):
        """
        Perform K-NN clustering for the selected symbols and features within a date range.
        Includes dimensionality reduction for visualizing clusters.
        """
        if not selected_symbols:
            raise ValueError("No symbols selected for clustering.")
        if not selected_features or len(selected_features) < 2:
            raise ValueError("Please select at least two features for clustering.")

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

        # Aggregate data to one row per symbol
        data = data.groupby("symbol").agg({
            "open": "mean",
            "high": "mean",
            "low": "mean",
            "close": "mean",
            "volume": "sum"
        }).reset_index()

        # Filter only selected features
        features = data[selected_features].dropna()
        feature_indices = features.index  # Save the indices of rows with valid features
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)

        # Perform K-Means clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        cluster_ids = kmeans.fit_predict(features_normalized)

        # Perform dimensionality reduction if selected
        if reduction_method != "none":
            if features_normalized.shape[0] < 2:
                raise ValueError("Not enough data points for dimensionality reduction.")

            try:
                if reduction_method == "tsne":
                    reducer = TSNE(n_components=2, perplexity=min(30, features_normalized.shape[0] // 2), random_state=42)
                elif reduction_method == "pca":
                    reducer = PCA(n_components=2)
                else:
                    raise ValueError("Unsupported reduction method. Choose 'tsne' or 'pca'.")

                reduced_data = reducer.fit_transform(features_normalized)
            except Exception as e:
                raise ValueError(f"Dimensionality reduction failed: {e}")

            # Align reduced dimensions to the DataFrame
            data["x"] = reduced_data[:, 0]
            data["y"] = reduced_data[:, 1]
        else:
            # No dimensionality reduction; fallback to default cluster visualization
            data["x"] = features_normalized[:, 0]
            data["y"] = features_normalized[:, 1]

        # Align cluster IDs and reduced dimensions back to the original DataFrame
        data = data.loc[feature_indices].copy()
        data["cluster_id"] = cluster_ids
        data["x"] = reduced_data[:, 0]
        data["y"] = reduced_data[:, 1]

        # Prepare results for insertion
        clustering_results = []
        for _, row in data.iterrows():
            result_data = {
                "features": row[selected_features].to_dict(),
                "cluster_center": kmeans.cluster_centers_[int(row["cluster_id"])].tolist(),
                "reduced_dimensions": {"x": row["x"], "y": row["y"]}
            }
            clustering_results.append((
                row["symbol"],
                "knn_clustering",
                int(row["cluster_id"]),
                json.dumps(result_data)  # Serialize dict to JSON string
            ))

        # Debugging: Check number of records to insert
        print(f"DEBUG: Prepared {len(clustering_results)} clustering results for insertion.")

        insert_clustering_results(clustering_results)
        print(f"✅ Stored K-NN clustering results for {len(data)} rows.")
        return data

    @staticmethod
    def perform_graph_clustering(selected_symbols, start_date, end_date, selected_features):
        """
        Perform graph-based clustering using selected features.
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
    def plot_cluster_dashboard(results):
        """
        Enhanced visualization for K-NN clustering with multiple subplots, including scatter plot, 
        bar chart for cluster sizes, and heatmap of cluster distances.
        """
        # Parse and extract reduced dimensions and cluster centers
        results["parsed_results"] = results["result"].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x
        )
        results["x"] = results["parsed_results"].apply(lambda r: r.get("reduced_dimensions", {}).get("x", None))
        results["y"] = results["parsed_results"].apply(lambda r: r.get("reduced_dimensions", {}).get("y", None))
        results["cluster_center"] = results["parsed_results"].apply(lambda r: r.get("cluster_center", None))

        if results["x"].isnull().all() or results["y"].isnull().all():
            raise ValueError("No valid reduced dimensions found for visualization.")

        # Scatter Plot with Clusters
        scatter_fig = go.Figure()
        for cluster_id, cluster_data in results.groupby("cluster_id"):
            scatter_fig.add_trace(
                go.Scatter(
                    x=cluster_data["x"],
                    y=cluster_data["y"],
                    mode="markers",
                    name=f"Cluster {cluster_id}",
                    marker=dict(
                        size=10,
                        color=cluster_id,
                        colorscale="Viridis",
                        line=dict(width=1, color="DarkSlateGrey"),
                    ),
                    text=[
                        f"Symbol: {row['symbol']}<br>Cluster ID: {cluster_id}<br>Features: {row['parsed_results']['features']}"
                        for _, row in cluster_data.iterrows()
                    ],
                    hoverinfo="text",
                )
            )

            # Add cluster centroid markers
            centroid = cluster_data["cluster_center"].iloc[0]
            if centroid:
                scatter_fig.add_trace(
                    go.Scatter(
                        x=[centroid[0]],
                        y=[centroid[1]],
                        mode="markers+text",
                        name=f"Centroid {cluster_id}",
                        marker=dict(
                            size=15,
                            color="red",
                            symbol="x",
                            line=dict(width=2, color="black"),
                        ),
                        text=[f"Centroid<br>Cluster {cluster_id}"],
                        textposition="top center",
                        hoverinfo="text",
                    )
                )

        scatter_fig.update_layout(
            title="Cluster Visualization (Scatter Plot)",
            xaxis=dict(title="Dimension 1"),
            yaxis=dict(title="Dimension 2"),
            template="plotly_white",
            dragmode="pan",
        )

        # Bar Chart for Cluster Sizes
        cluster_sizes = results["cluster_id"].value_counts()
        bar_fig = go.Figure()
        bar_fig.add_trace(
            go.Bar(
                x=cluster_sizes.index.astype(str),
                y=cluster_sizes.values,
                name="Cluster Sizes",
                marker=dict(color="purple"),
                text=[f"Cluster {i}: {size} points" for i, size in zip(cluster_sizes.index, cluster_sizes.values)],
                hoverinfo="text",
            )
        )
        bar_fig.update_layout(
            title="Cluster Size Distribution",
            xaxis=dict(title="Cluster ID"),
            yaxis=dict(title="Number of Points"),
            template="plotly_white",
        )

        # Heatmap of Distances Between Cluster Centers
        cluster_centers = results.groupby("cluster_id")["cluster_center"].first().dropna()
        cluster_centers = np.array([np.array(center) for center in cluster_centers])
        if cluster_centers.size > 0:
            distances = np.linalg.norm(
                cluster_centers[:, np.newaxis] - cluster_centers, axis=2
            )
            heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=distances,
                    x=[f"Cluster {i}" for i in range(len(cluster_centers))],
                    y=[f"Cluster {i}" for i in range(len(cluster_centers))],
                    colorscale="Blues",
                )
            )
            heatmap_fig.update_layout(
                title="Inter-Cluster Distance Heatmap",
                xaxis=dict(title="Cluster"),
                yaxis=dict(title="Cluster"),
                template="plotly_white",
            )
        else:
            heatmap_fig = go.Figure()
            heatmap_fig.update_layout(
                title="Inter-Cluster Distance Heatmap (No Data)",
                template="plotly_white",
            )

        return scatter_fig, bar_fig, heatmap_fig

    @staticmethod
    def _calculate_ellipse(mean_x, mean_y, covariance_matrix, n_std=2.0, resolution=100):
        """
        Generate a confidence ellipse for cluster visualization.
        """
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
        order = eigenvalues.argsort()[::-1]
        eigenvalues, eigenvectors = eigenvalues[order], eigenvectors[:, order]

        # Compute width, height, and angle of the ellipse
        theta = np.linspace(0, 2 * np.pi, resolution)
        width, height = 2 * n_std * np.sqrt(eigenvalues)
        angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1]))

        # Parametric ellipse equation
        ellipse_coords = np.array([np.cos(theta) * width, np.sin(theta) * height])
        rotation_matrix = np.array([[np.cos(np.radians(angle)), -np.sin(np.radians(angle))],
                                    [np.sin(np.radians(angle)), np.cos(np.radians(angle))]])
        rotated_coords = rotation_matrix @ ellipse_coords
        ellipse_x, ellipse_y = rotated_coords[0] + mean_x, rotated_coords[1] + mean_y

        return go.Scatter(
            x=ellipse_x,
            y=ellipse_y,
            mode="lines",
            name="Confidence Ellipse",
            line=dict(color="rgba(0,100,80,0.2)", width=2),
            hoverinfo="skip"
        )

    @staticmethod
    def plot_graph_clusters(results):
        """
        Visualize graph-based clusters with enhanced interactivity and grid markers.
        """
        graph = nx.Graph()

        # Build the graph using data from the 'result' column
        for _, row in results.iterrows():
            result_data = row["result"]
            connected_symbols = result_data.get("connected_symbols", [])
            for symbol in connected_symbols:
                graph.add_edge(row["symbol"], symbol)

        # Calculate graph metrics
        centrality = nx.degree_centrality(graph)
        clustering_coeff = nx.clustering(graph)
        betweenness = nx.betweenness_centrality(graph)

        # Community detection
        communities = list(greedy_modularity_communities(graph))
        community_map = {node: i for i, community in enumerate(communities) for node in community}

        # Assign node attributes
        for node in graph.nodes():
            graph.nodes[node]["centrality"] = centrality.get(node, 0)
            graph.nodes[node]["clustering_coeff"] = clustering_coeff.get(node, 0)
            graph.nodes[node]["betweenness"] = betweenness.get(node, 0)
            graph.nodes[node]["community"] = community_map.get(node, -1)

        # Generate layout
        pos = nx.spring_layout(graph)

        # Prepare edge data
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

        # Prepare node data
        node_x = []
        node_y = []
        node_size = []
        node_color = []
        node_text = []

        for node in graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_size.append(10 + 30 * centrality[node])  # Scale size by centrality
            node_color.append(community_map[node])  # Color by community
            node_text.append(
                f"Node: {node}<br>"
                f"Community: {community_map[node]}<br>"
                f"Degree: {graph.degree[node]}<br>"
                f"Centrality: {centrality[node]:.2f}<br>"
                f"Clustering Coefficient: {clustering_coeff[node]:.2f}<br>"
                f"Betweenness: {betweenness[node]:.2f}"
            )

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            mode="markers",
            hoverinfo="text",
            marker=dict(
                showscale=True,
                colorscale="Viridis",
                size=node_size,
                color=node_color,
                colorbar=dict(
                    title="Community",
                    thickness=15,
                    xanchor="left",
                    titleside="right",
                ),
                line=dict(width=1, color="black"),
            ),
        )

        # Adding grid markers
        layout = go.Layout(
            title="Interactive Graph-Based Clustering",
            title_x=0.5,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=40, l=40, r=40, t=40),
            xaxis=dict(
                showgrid=True,  # Enable grid
                zeroline=False,
                showticklabels=False,
            ),
            yaxis=dict(
                showgrid=True,  # Enable grid
                zeroline=False,
                showticklabels=False,
            ),
            dragmode="pan",  # Allow dragging/panning
        )

        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

        # Enable clicking into clusters (optional, can be extended to a callback system)
        fig.update_traces(
            selector=dict(mode="markers"),
            customdata=node_text,
        )

        return fig
    