import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from plotly.graph_objs import Scatter, Figure
from src.utils.database import connect_to_db

def perform_clustering_analysis(symbols=None):
    """
    Performs clustering on company data and returns a visualization.
    If data is missing, it fetches raw data and populates the required columns.
    """
    conn = connect_to_db()

    # Check if data exists for clustering
    check_query = "SELECT COUNT(*) FROM company_analysis WHERE log_returns IS NOT NULL AND pe_ratio IS NOT NULL AND market_cap IS NOT NULL"
    result = pd.read_sql_query(check_query, conn)
    if result.iloc[0, 0] == 0:
        print("ℹ️ No data available for clustering. Fetching raw data to populate required columns...")
        populate_clustering_data(conn)

    query = """
    SELECT symbol, log_returns, pe_ratio, market_cap
    FROM company_analysis
    """
    if symbols:
        symbol_filter = ",".join([f"'{s}'" for s in symbols])
        query += f" WHERE symbol IN ({symbol_filter})"

    # Fetch data
    data = pd.read_sql_query(query, conn)
    if data.empty:
        print("⚠️ No data available for clustering analysis after populating.")
        conn.close()
        return Figure()  # Return an empty figure for the dashboard

    # Preprocessing: Scale features
    features = ["log_returns", "pe_ratio", "market_cap"]
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data[features])

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    data["cluster"] = kmeans.fit_predict(data_scaled)

    # Save cluster results back to the database
    for _, row in data.iterrows():
        conn.execute("""
        UPDATE company_analysis
        SET cluster_id = %s
        WHERE symbol = %s
        """, (int(row["cluster"]), row["symbol"]))
    conn.commit()
    conn.close()

    print("✅ Clustering analysis results stored in the database.")

    # Generate visualization
    figure = Figure()
    for cluster in data["cluster"].unique():
        cluster_data = data[data["cluster"] == cluster]
        figure.add_trace(Scatter(
            x=cluster_data["log_returns"],
            y=cluster_data["market_cap"],
            mode="markers",
            name=f"Cluster {cluster}",
            marker=dict(size=10)
        ))

    figure.update_layout(
        title="Clustering Analysis",
        xaxis_title="Log Returns",
        yaxis_title="Market Cap",
        template="plotly_white"
    )
    return figure


def populate_clustering_data(conn):
    """
    Populates the company_analysis table with derived columns needed for clustering.
    Fetches raw data from historical and real-time data tables.
    """
    # Fetch raw data from historical and real-time tables
    historical_query = """
    SELECT symbol, datetime, close, open, 
           (market_cap / pe_ratio) AS pe_ratio, market_cap
    FROM historical_market_data
    WHERE close IS NOT NULL AND open IS NOT NULL
    """
    real_time_query = """
    SELECT symbol, datetime, close, open, 
           (market_cap / pe_ratio) AS pe_ratio, market_cap
    FROM real_time_market_data
    WHERE close IS NOT NULL AND open IS NOT NULL
    """

    historical_data = pd.read_sql_query(historical_query, conn)
    real_time_data = pd.read_sql_query(real_time_query, conn)

    if historical_data.empty and real_time_data.empty:
        print("⚠️ No raw data available in historical or real-time tables.")
        return

    # Combine historical and real-time data
    raw_data = pd.concat([historical_data, real_time_data])

    # Compute log returns
    raw_data["log_returns"] = (raw_data["close"] / raw_data["open"]).apply(np.log)

    # Insert derived data into company_analysis table
    for _, row in raw_data.iterrows():
        conn.execute("""
        INSERT INTO company_analysis (symbol, datetime, log_returns, pe_ratio, market_cap)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (symbol, datetime) DO UPDATE
        SET log_returns = EXCLUDED.log_returns,
            pe_ratio = EXCLUDED.pe_ratio,
            market_cap = EXCLUDED.market_cap
        """, (row["symbol"], row["datetime"], row["log_returns"], row["pe_ratio"], row["market_cap"]))
    conn.commit()
    print("✅ Populated company_analysis table with data from historical and real-time tables.")
    
