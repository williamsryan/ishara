from dash import dcc, html
import plotly.graph_objs as go
import networkx as nx
from src.utils.database import connect_to_db
import pandas as pd

class PriceChart:
    def layout(self, symbols, start_date, end_date):
        conn = connect_to_db()
        query = f"""
            SELECT datetime, close, symbol
            FROM historical_market_data
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
              AND datetime BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY datetime ASC
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return html.Div("⚠️ No price data available for the selected criteria.")

        figure = go.Figure()
        for symbol in symbols:
            symbol_data = data[data["symbol"] == symbol]
            figure.add_trace(go.Scatter(x=symbol_data["datetime"], y=symbol_data["close"],
                                        mode="lines", name=f"{symbol} Price"))

        figure.update_layout(title="Price Chart", template="plotly_white")
        return dcc.Graph(figure=figure)

class AlternativeDataCharts:
    def layout(self, symbols, start_date, end_date, overlay_toggle):
        conn = connect_to_db()
        query = f"""
            SELECT datetime, value, metric, symbol
            FROM alternative_data
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
              AND datetime BETWEEN '{start_date}' AND '{end_date}'
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return html.Div("⚠️ No alternative data available.")

        figures = []
        for metric in data["metric"].unique():
            metric_data = data[data["metric"] == metric]
            fig = go.Figure()
            for symbol in symbols:
                symbol_data = metric_data[metric_data["symbol"] == symbol]
                fig.add_trace(go.Scatter(x=symbol_data["datetime"], y=symbol_data["value"],
                                         mode="lines", name=f"{symbol} {metric}"))

            fig.update_layout(title=f"{metric.capitalize()} Over Time", template="plotly_white")
            figures.append(dcc.Graph(figure=fig))

        return html.Div(figures)

class KnnClusteringChart:
    def layout(self):
        conn = connect_to_db()
        query = """
            SELECT result
            FROM analysis_results
            WHERE analysis_type = 'clustering_knn'
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return html.Div("⚠️ No K-NN clustering results available.")

        results = pd.json_normalize([pd.read_json(row["result"]) for _, row in data.iterrows()])
        fig = go.Figure()
        for cluster_id in results['cluster'].unique():
            cluster_data = results[results['cluster'] == cluster_id]
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
        conn = connect_to_db()
        query = """
            SELECT result
            FROM analysis_results
            WHERE analysis_type = 'clustering_graph'
        """
        data = pd.read_sql(query, conn)

        if data.empty:
            return html.Div("⚠️ No graph-based clustering results available.")

        results = pd.json_normalize([pd.read_json(row["result"]) for _, row in data.iterrows()])

        G = nx.Graph()
        for _, row in results.iterrows():
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
    