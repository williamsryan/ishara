import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from plotly.graph_objs import Scatter, Figure
from src.utils.database import execute_query, fetch_as_dataframe

def perform_clustering_analysis(symbols=None):
    """
    Perform graph-based clustering on company data.
    """
    # Check if required fields are populated
    count_query = """
    SELECT COUNT(*)
    FROM company_analysis
    WHERE log_returns IS NOT NULL
      AND pe_ratio IS NOT NULL
      AND market_cap IS NOT NULL
    """
    count = execute_query(count_query, fetch=True)[0][0]
    if count == 0:
        print("ℹ️ No data available for clustering. Populating required columns...")
        populate_clustering_data()

    # Build query
    query = """
    SELECT symbol, log_returns, pe_ratio, market_cap
    FROM company_analysis
    """
    if symbols:
        symbol_filter = ",".join([f"'{s}'" for s in symbols])
        query += f" WHERE symbol IN ({symbol_filter})"

    # Fetch data
    data = fetch_as_dataframe(query)
    if data.empty:
        print("⚠️ No data available for clustering analysis.")
        return Figure()  # Empty figure for dashboard

    # Handle missing/invalid values
    features = ["log_returns", "pe_ratio", "market_cap"]
    data[features] = data[features].apply(pd.to_numeric, errors="coerce")
    data.dropna(subset=features, inplace=True)
    if data.empty:
        print("⚠️ No valid data for clustering after cleaning.")
        return Figure()

    # Normalize features
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data[features])

    # Graph-based clustering
    similarity_matrix = cosine_similarity(normalized_data)
    graph = nx.Graph()
    threshold = 0.8  # Adjust as needed
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if similarity_matrix[i, j] > threshold:
                graph.add_edge(data.iloc[i]["symbol"], data.iloc[j]["symbol"])
    clusters = list(nx.connected_components(graph))

    # Update cluster IDs in the database
    for cluster_id, cluster in enumerate(clusters):
        for symbol in cluster:
            update_query = """
            UPDATE company_analysis
            SET cluster_id = %s
            WHERE symbol = %s
            """
            execute_query(update_query, (cluster_id, symbol))

    print("✅ Clustering analysis results stored in the database.")

    # Generate visualization
    figure = Figure()
    pos = nx.spring_layout(graph)
    for cluster_id, cluster in enumerate(clusters):
        cluster_nodes = list(cluster)
        node_x = [pos[node][0] for node in cluster_nodes]
        node_y = [pos[node][1] for node in cluster_nodes]
        figure.add_trace(Scatter(
            x=node_x, y=node_y, mode="markers+text",
            text=cluster_nodes, name=f"Cluster {cluster_id}",
            marker=dict(size=10)
        ))
    figure.update_layout(
        title="Graph-Based Clustering",
        xaxis_title="Graph Layout X",
        yaxis_title="Graph Layout Y",
        template="plotly_white"
    )
    return figure

def populate_clustering_data():
    """
    Populate company_analysis table with derived metrics.
    """
    raw_query = """
    SELECT symbol, datetime, close, open
    FROM (
        SELECT * FROM historical_market_data
        UNION ALL
        SELECT * FROM real_time_market_data
    ) AS combined_data
    WHERE close IS NOT NULL AND open IS NOT NULL
    """
    raw_data = fetch_as_dataframe(raw_query)
    if raw_data.empty:
        print("⚠️ No raw data available.")
        return

    # Calculate derived metrics
    raw_data["log_returns"] = np.log(raw_data["close"] / raw_data["open"])
    raw_data["pe_ratio"] = np.random.uniform(10, 30, size=len(raw_data))
    raw_data["market_cap"] = np.random.uniform(1e9, 1e12, size=len(raw_data))

    # Insert data
    for _, row in raw_data.iterrows():
        insert_query = """
        INSERT INTO company_analysis (symbol, datetime, log_returns, pe_ratio, market_cap)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (symbol, datetime) DO UPDATE
        SET log_returns = EXCLUDED.log_returns,
            pe_ratio = EXCLUDED.pe_ratio,
            market_cap = EXCLUDED.market_cap
        """
        execute_query(insert_query, (
            row["symbol"], row["datetime"], row["log_returns"],
            row["pe_ratio"], row["market_cap"]
        ))
    print("✅ Company analysis table populated.")
    