import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from src.utils.database import connect_to_db

def perform_clustering_analysis():
    conn = connect_to_db()
    query = """
    SELECT symbol, log_returns, pe_ratio, market_cap
    FROM company_analysis
    """
    data = pd.read_sql_query(query, conn)
    conn.close()

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
    