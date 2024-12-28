import pandas as pd
from src.utils.database import connect_to_db

def fetch_feature_data():
    """
    Fetch feature data for K-NN clustering.
    """
    conn = connect_to_db()
    query = """
        SELECT symbol, feature1, feature2
        FROM feature_table
    """
    data = pd.read_sql(query, conn)

    if data.empty:
        raise ValueError("No feature data available for clustering.")
    return data

def fetch_graph_data():
    """
    Fetch graph data for graph-based clustering.
    """
    conn = connect_to_db()
    query = """
        SELECT source, target, weight
        FROM graph_edges_table
    """
    data = pd.read_sql(query, conn)

    if data.empty:
        raise ValueError("No graph data available for clustering.")
    return data.to_dict(orient="records")
