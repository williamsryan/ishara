import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import json
from networkx.algorithms.community import greedy_modularity_communities
from src.utils.database import fetch_as_dataframe, insert_clustering_results

def perform_clustering_analysis():
    """
    Perform clustering and graph analysis on market data and store results in the analysis_results table.
    """
    # Fetch and merge data
    historical_query = """
    SELECT symbol, datetime, close, open
    FROM historical_market_data
    WHERE close IS NOT NULL AND open IS NOT NULL
    """
    historical_data = fetch_as_dataframe(historical_query)
    if historical_data.empty:
        print("⚠️ No historical data available for clustering analysis.")
        return

    options_query = """
    SELECT symbol, implied_volatility, open_interest, strike
    FROM options_data
    WHERE implied_volatility IS NOT NULL AND open_interest IS NOT NULL
    """
    options_data = fetch_as_dataframe(options_query)
    if options_data.empty:
        print("⚠️ No options data available for clustering analysis.")
        return

    # Calculate derived metrics
    historical_data["log_returns"] = np.log(historical_data["close"] / historical_data["open"])
    historical_features = historical_data.groupby("symbol").agg({
        "log_returns": "mean"
    }).reset_index()

    options_features = options_data.groupby("symbol").agg({
        "implied_volatility": "mean",
        "open_interest": "sum",
        "strike": "mean"
    }).reset_index()

    derived_data = pd.merge(historical_features, options_features, on="symbol", how="inner")
    if derived_data.empty:
        print("⚠️ No combined data available for clustering analysis.")
        return

    # Normalize features
    features = ["log_returns", "implied_volatility", "open_interest", "strike"]
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(derived_data[features])

    # Perform graph-based clustering using cosine similarity
    similarity_matrix = cosine_similarity(normalized_data)
    graph = nx.Graph()
    threshold = 0.8  # Adjust threshold for similarity
    for i in range(len(derived_data)):
        for j in range(i + 1, len(derived_data)):
            if similarity_matrix[i, j] > threshold:
                graph.add_edge(derived_data.iloc[i]["symbol"], derived_data.iloc[j]["symbol"])

    # Compute graph metrics
    centrality = nx.degree_centrality(graph)
    clustering_coefficient = nx.clustering(graph)

    # Detect clusters (connected components)
    clusters = list(nx.connected_components(graph))

    # Insert graph clustering results
    graph_clustering_results = []
    for cluster_id, cluster in enumerate(clusters):
        for symbol in cluster:
            result_data = {
                "connected_symbols": list(cluster),
                "centrality": centrality[symbol],
                "clustering_coefficient": clustering_coefficient[symbol],
            }
            graph_clustering_results.append((
                symbol,
                "graph_clustering",
                cluster_id,
                json.dumps(result_data)
            ))

    if graph_clustering_results:
        insert_clustering_results(graph_clustering_results)
        print(f"✅ Stored graph clustering results for {len(clusters)} clusters.")
    else:
        print("⚠️ No graph clustering results to store.")

    # Perform community detection
    communities = list(greedy_modularity_communities(graph))

    # Insert community detection results
    community_detection_results = []
    for community_id, community in enumerate(communities):
        for symbol in community:
            result_data = {
                "community_members": list(community),
                "community_size": len(community),
                "average_centrality": np.mean([centrality[node] for node in community]),
                "average_clustering_coefficient": np.mean([clustering_coefficient[node] for node in community]),
            }
            community_detection_results.append((
                symbol,
                "community_detection",
                community_id,
                json.dumps(result_data)
            ))

    if community_detection_results:
        insert_clustering_results(community_detection_results)
        print(f"✅ Stored community detection results for {len(communities)} communities.")
    else:
        print("⚠️ No community detection results to store.")

if __name__ == "__main__":
    perform_clustering_analysis()
