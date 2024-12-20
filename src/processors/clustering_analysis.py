import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from plotly.graph_objs import Scatter, Figure
from src.utils.database import connect_to_db

def perform_clustering_analysis(symbols=None):
    """
    Performs clustering on company data and returns a visualization.
    """
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if data exists for clustering
    check_query = """
    SELECT COUNT(*)
    FROM company_analysis
    WHERE log_returns IS NOT NULL
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

    # Preprocessing: Scale features
    features = ["log_returns", "pe_ratio", "market_cap"]
    data[features] = data[features].astype(float)  # Ensure all values are float
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data[features])

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    data["cluster"] = kmeans.fit_predict(data_scaled)

    # Save cluster results back to the database
    for _, row in data.iterrows():
        cursor.execute("""
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
    try:
        cursor = conn.cursor()

        # Fetch raw data from historical and real-time tables
        historical_query = """
        SELECT symbol, datetime, close, open
        FROM historical_market_data
        WHERE close IS NOT NULL AND open IS NOT NULL
        """
        real_time_query = """
        SELECT symbol, datetime, close, open
        FROM real_time_market_data
        WHERE close IS NOT NULL AND open IS NOT NULL
        """

        cursor.execute(historical_query)
        historical_data = cursor.fetchall()
        cursor.execute(real_time_query)
        real_time_data = cursor.fetchall()

        # Check if data is available
        if not historical_data and not real_time_data:
            print("⚠️ No raw data available in historical or real-time tables.")
            return

        # Combine historical and real-time data
        columns = ["symbol", "datetime", "close", "open"]
        raw_data = pd.DataFrame(historical_data + real_time_data, columns=columns)

        # Convert decimal.Decimal to float
        raw_data["close"] = raw_data["close"].astype(float)
        raw_data["open"] = raw_data["open"].astype(float)

        # Compute log returns
        raw_data["log_returns"] = (raw_data["close"] / raw_data["open"]).apply(np.log)

        # Insert derived data into company_analysis table
        for _, row in raw_data.iterrows():
            try:
                cursor.execute("""
                INSERT INTO company_analysis (symbol, datetime, log_returns)
                VALUES (%s, %s, %s)
                ON CONFLICT (symbol, datetime) DO UPDATE
                SET log_returns = EXCLUDED.log_returns
                """, (row["symbol"], row["datetime"], row["log_returns"]))
            except Exception as e:
                print(f"❌ Error inserting row for {row['symbol']}: {e}")
                conn.rollback()  # Roll back only the failed row

        conn.commit()
        print("✅ Populated company_analysis table with data from historical and real-time tables.")

    except Exception as e:
        print(f"❌ Error populating clustering data: {e}")
        conn.rollback()  # Roll back the entire transaction
    finally:
        cursor.close()
