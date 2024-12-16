import plotly.graph_objects as go
import plotly.io as pio

def plot_portfolio_performance(portfolio_results, portfolio):
    """
    Plot portfolio performance and individual stock equity curves.

    Args:
        portfolio_results (dict): Results from portfolio backtesting.
        portfolio (dict): Portfolio stocks and weights.
    """
    # Extract portfolio value and time series
    portfolio_value = portfolio_results["portfolio_value"]
    time_series = portfolio_results["time_series"]

    # Create portfolio value plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_series, y=portfolio_value, mode='lines', name='Portfolio Value'))

    # Customize layout
    fig.update_layout(
        title="Portfolio Performance",
        xaxis_title="Time",
        yaxis_title="Portfolio Value",
        legend_title="Assets",
    )

    # Show the interactive plot
    pio.show(fig)  # Ensures the figure remains open
    