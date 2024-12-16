import subprocess
import json
import os

def run_backtest(project_name, output_dir="lean/backtest_results"):
    """
    Run a backtest for a specific Lean project and save results.

    Args:
        project_name (str): Name of the Lean project.
        output_dir (str): Directory to save backtest results.

    Returns:
        dict: Backtest statistics.
    """
    os.makedirs(output_dir, exist_ok=True)
    result_file = os.path.join(output_dir, f"{project_name}_results.json")

    # Run the Lean backtest command
    subprocess.run(["lean", "backtest", project_name, "--output", result_file], check=True)

    # Parse the backtest results
    with open(result_file, "r") as f:
        results = json.load(f)

    # Extract statistics
    stats = results["Statistics"]
    return {
        "Project": project_name,
        "Total Return": stats["Total Return"],
        "Sharpe Ratio": stats["Sharpe Ratio"],
        "Max Drawdown": stats["Drawdown"]
    }

def compare_strategies(projects):
    """
    Run backtests for multiple projects and compare results.

    Args:
        projects (list): List of Lean project names.
    """
    results = []
    for project in projects:
        print(f"Running backtest for {project}...")
        stats = run_backtest(project)
        results.append(stats)

    # Print summary
    print("\nComparison of Strategies:")
    for result in results:
        print(result)

if __name__ == "__main__":
    strategies = ["MomentumSectorRotation", "MovingAverageCrossover"]
    compare_strategies(strategies)
    