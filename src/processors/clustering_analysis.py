import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from plotly.graph_objs import Scatter, Figure
from src.utils.database import connect_to_db

def perform_clustering_analysis(symbols=None):
    """
    Performs graph-based clustering on company data and returns a visualization.
    """
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if all necessary fields are populated
    check_query = """
    SELECT COUNT(*)
    FROM company_analysis
    WHERE log_returns IS NOT NULL
      AND pe_ratio IS NOT NULL
      AND market_cap IS NOT NULL
    """
    cursor.execute(check_query)
    count = cursor.fetchone()[0]
    if count == 0:
        print("ℹ️ No data available for clustering. Fetching raw data to populate required columns...")
        populate_clustering_data(conn)

    # Build the query
    query = """
    SELECT symbol, log_returns, pe_ratio, market_cap
    FROM company_analysis
    """
    if symbols:
        symbol_filter = ",".join([f"'{s}'" for s in symbols])
        query += f" WHERE symbol IN ({symbol_filter})"

    # Fetch data and convert to DataFrame
    cursor.execute(query)
    rows = cursor.fetchall()
    if not rows:
        print("⚠️ No data available for clustering analysis after populating.")
        conn.close()
        return Figure()  # Return an empty figure for the dashboard

    columns = [desc[0] for desc in cursor.description]
    data = pd.DataFrame(rows, columns=columns)

    # Handle missing or invalid values
    features = ["log_returns", "pe_ratio", "market_cap"]
    data[features] = data[features].apply(pd.to_numeric, errors="coerce")
    data = data.dropna(subset=features)

    if data.empty:
        print("⚠️ No valid data available for clustering after cleaning.")
        conn.close()
        return Figure()  # Return an empty figure for the dashboard

    # Normalize features
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data[features])

    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(normalized_data)

    # Create a graph based on similarity
    graph = nx.Graph()
    threshold = 0.8  # Adjust threshold as needed
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if similarity_matrix[i, j] > threshold:
                graph.add_edge(data.iloc[i]["symbol"], data.iloc[j]["symbol"])

    # Identify clusters (connected components)
    clusters = list(nx.connected_components(graph))

    # Store cluster results in the database
    for cluster_id, cluster in enumerate(clusters):
        for symbol in cluster:
            cursor.execute("""
            UPDATE company_analysis
            SET cluster_id = %s
            WHERE symbol = %s
            """, (cluster_id, symbol))
    conn.commit()

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
    conn.close()
    return figure

def populate_clustering_data(conn):
    """
    Populates the company_analysis table with derived columns needed for clustering.
    Fetches raw data and computes derived metrics.
    """
    try:
        cursor = conn.cursor()

        # Fetch raw data from historical and real-time tables
        query = """
        SELECT symbol, datetime, close, open
        FROM (
            SELECT * FROM historical_market_data
            UNION ALL
            SELECT * FROM real_time_market_data
        ) AS combined_data
        WHERE close IS NOT NULL AND open IS NOT NULL
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = ["symbol", "datetime", "close", "open"]
        raw_data = pd.DataFrame(rows, columns=columns)

        if raw_data.empty:
            print("⚠️ No raw data available for clustering.")
            return

        # Convert numeric fields and compute derived metrics
        raw_data["close"] = raw_data["close"].astype(float)
        raw_data["open"] = raw_data["open"].astype(float)
        raw_data["log_returns"] = (raw_data["close"] / raw_data["open"]).apply(np.log)

        # Fetch or calculate placeholders for P/E ratio and market cap
        raw_data["pe_ratio"] = np.random.uniform(10, 30, size=len(raw_data))  # Replace with actual logic
        raw_data["market_cap"] = np.random.uniform(1e9, 1e12, size=len(raw_data))  # Replace with actual logic

        # Batch insert into company_analysis table
        for _, row in raw_data.iterrows():
            cursor.execute("""
            INSERT INTO company_analysis (symbol, datetime, log_returns, pe_ratio, market_cap)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (symbol, datetime) DO UPDATE
            SET log_returns = EXCLUDED.log_returns,
                pe_ratio = EXCLUDED.pe_ratio,
                market_cap = EXCLUDED.market_cap
            """, (row["symbol"], row["datetime"], row["log_returns"], row["pe_ratio"], row["market_cap"]))
        conn.commit()

        print("✅ Populated company_analysis table with derived metrics.")
    except Exception as e:
        print(f"❌ Error populating clustering data: {e}")
        conn.rollback()
    finally:
        cursor.close()
