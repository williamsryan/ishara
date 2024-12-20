import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from plotly.graph_objs import Scatter, Figure
from src.utils.database import connect_to_db

def perform_clustering_analysis(symbols=None):
    """
    Performs clustering on company data and returns a visualization.
    Updates cluster IDs back to the database.
    """
    conn = connect_to_db()
    query = """
    SELECT symbol, log_returns, pe_ratio, market_cap
    FROM company_analysis
    """
    if symbols:
        symbol_filter = ",".join([f"'{s}'" for s in symbols])
        query += f" WHERE symbol IN ({symbol_filter})"

    data = pd.read_sql_query(query, conn)
    conn.close()

    if data.empty:
        print("⚠️ No data available for clustering analysis.")
        return Figure()  # Return an empty figure for the dashboard

    # Preprocessing: Scale features
    features = ["log_returns", "pe_ratio", "market_cap"]
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data[features])

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    data["cluster"] = kmeans.fit_predict(data_scaled)

    # Save results back to the database
    conn = connect_to_db()
    for _, row in data.iterrows():
        conn.execute("""
        UPDATE company_analysis
        SET cluster_id = %s
        WHERE symbol = %s
        """, (row["cluster"], row["symbol"]))
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
            name=f"Cluster {cluster}"
        ))

    figure.update_layout(
        title="Clustering Analysis",
        xaxis_title="Log Returns",
        yaxis_title="Market Cap",
        template="plotly_dark"
    )
    return figure
