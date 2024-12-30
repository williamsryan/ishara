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
            FROM {data_source} 
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
            ORDER BY datetime ASC
        """
        # params = tuple(symbols) + (start_date, end_date)
        results = fetch_data(query, params=tuple(symbols,))

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
    def layout(self, symbols):
        # Fetch data
        query = f"""
            SELECT datetime, metric, value, symbol
            FROM alternative_data
            WHERE symbol IN ({','.join(['%s'] * len(symbols))})
        """
        results = fetch_data(query, params=tuple(symbols))

        if results.empty:
            return html.Div("⚠️ No alternative data available for the selected symbols.", className="text-warning p-3")

        # Generate metric options dynamically
        metrics = results["metric"].unique()
        metric_options = [{"label": metric.capitalize(), "value": metric} for metric in metrics]

        # Controls for metric selection
        controls = html.Div([
            html.Label("Select Metrics to Display"),
            dcc.Checklist(
                id="metric-filter",
                options=metric_options,
                value=metrics.tolist(),  # Default to all metrics
                inline=True
            )
        ], className="mb-4")

        # Placeholder for graphs
        graphs_container = html.Div(id="alternative-data-graphs")

        return html.Div([controls, graphs_container], className="container")
    
    def render_graphs(self, symbols, selected_metrics):
        # Fetch data for the selected symbols and metrics
        query = f"""
            SELECT datetime, metric, value, symbol
            FROM alternative_data
            WHERE symbol IN ({','.join(['%s'] * len(symbols))}) AND metric = ANY(%s)
        """
        params = tuple(symbols) + (selected_metrics,)
        results = fetch_data(query, params=params)

        if results.empty:
            return html.Div("⚠️ No data available for the selected metrics.", className="text-warning p-3")

        # Generate a graph for each selected metric
        graphs = []
        for metric in selected_metrics:
            metric_data = results[results["metric"] == metric]
            fig = go.Figure()
            for symbol in symbols:
                symbol_data = metric_data[metric_data["symbol"] == symbol]
                fig.add_trace(go.Scatter(
                    x=symbol_data["datetime"], y=symbol_data["value"],
                    mode="lines", name=f"{symbol} {metric}"
                ))
            fig.update_layout(
                title=f"{metric.capitalize()} Over Time",
                xaxis_title="Datetime",
                yaxis_title="Value"
            )
            graphs.append(dcc.Graph(figure=fig))

        return html.Div(graphs)

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
    