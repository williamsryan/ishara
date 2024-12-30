from dash import dcc, html
import plotly.graph_objs as go
import networkx as nx
from src.utils.database import fetch_data
import pandas as pd

class PriceChart:
    def layout(self, symbols, start_date, end_date, data_source):
        # Build the query dynamically based on the selected data source
        query = f"""
            SELECT datetime, close, symbol
            FROM {data_source}  -- Use the dynamic data source
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
            AND datetime BETWEEN %s AND %s
            ORDER BY datetime ASC
        """
        params = tuple(symbols) + (start_date, end_date)
        results = fetch_data(query, params=params)

        # Check if the DataFrame is empty
        if results.empty:
            return html.Div("⚠️ No price data available for the selected criteria.", className="text-warning p-3")

        figure = go.Figure()
        for symbol in symbols:
            symbol_data = results[results["symbol"] == symbol]
            figure.add_trace(go.Scatter(
                x=symbol_data["datetime"], y=symbol_data["close"], mode="lines", name=f"{symbol} Price"
            ))

        figure.update_layout(title="Price Chart", xaxis_title="Datetime", yaxis_title="Close Price")
        return dcc.Graph(figure=figure)

class AlternativeDataCharts:
    def layout(self, symbols, start_date, end_date, overlay_toggle, data_source):
        query = f"""
            SELECT datetime, metric, value
            FROM {data_source}
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
            AND datetime BETWEEN %s AND %s
        """
        params = tuple(symbols) + (start_date, end_date)
        results = fetch_data(query, params=params)

        if results.empty:
            return html.Div("⚠️ No alternative data available.", className="text-warning p-3")

        sentiment_figure = go.Figure()
        mentions_figure = go.Figure()

        for row in results.to_dict(orient="records"):
            if row["metric"] == "sentiment":
                sentiment_figure.add_trace(go.Scatter(x=row["datetime"], y=row["value"], mode="lines"))
            elif row["metric"] == "mentions":
                mentions_figure.add_trace(go.Bar(x=row["datetime"], y=row["value"]))

        return html.Div([
            dcc.Graph(figure=sentiment_figure),
            dcc.Graph(figure=mentions_figure),
        ])

class KnnClusteringChart:
    def layout(self):
        query = """
            SELECT result
            FROM analysis_results
            WHERE analysis_type = 'clustering_knn'
        """
        results = fetch_data(query)

        if not results:
            return html.Div("⚠️ No K-NN clustering results available.", className="text-warning p-3")

        # Parse and normalize JSON data
        parsed_results = pd.json_normalize([row["result"] for row in results])
        fig = go.Figure()
        for cluster_id in parsed_results['cluster'].unique():
            cluster_data = parsed_results[parsed_results['cluster'] == cluster_id]
            fig.add_trace(go.Scatter(
                x=cluster_data['feature1'], y=cluster_data['feature2'],
                mode='markers', name=f"Cluster {cluster_id}",
                marker=dict(size=10)
            ))

        fig.update_layout(
            title="K-NN Clustering Results",
            xaxis_title="Feature 1",
            yaxis_title="Feature 2",
            template="plotly_white"
        )
        return dcc.Graph(figure=fig)

class GraphClusteringChart:
    def layout(self):
        query = """
            SELECT result
            FROM analysis_results
            WHERE analysis_type = 'clustering_graph'
        """
        results = fetch_data(query)

        if not results:
            return html.Div("⚠️ No graph-based clustering results available.", className="text-warning p-3")

        # Parse and normalize JSON data
        parsed_results = pd.json_normalize([row["result"] for row in results])

        G = nx.Graph()
        for _, row in parsed_results.iterrows():
            G.add_node(row['symbol'], centrality=row['node_centrality'])

        pos = nx.spring_layout(G)
        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0.5, color='#888'),
            hoverinfo='none', mode='lines'
        )
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += [x0, x1, None]
            edge_trace['y'] += [y0, y1, None]

        node_trace = go.Scatter(
            x=[], y=[], mode='markers',
            marker=dict(size=[], color=[]),
            text=[]
        )
        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'].append(x)
            node_trace['y'].append(y)
            node_trace['marker']['size'].append(G.nodes[node]['centrality'] * 100)
            node_trace['marker']['color'].append(G.nodes[node]['centrality'])
            node_trace['text'].append(f"Node {node}<br>Centrality: {G.nodes[node]['centrality']}")

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="Graph-Based Clustering Results",
            showlegend=False,
            hovermode='closest',
            template="plotly_white"
        )
        return dcc.Graph(figure=fig)
    