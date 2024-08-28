import logging as Logger
import os
import sys

# Ensure the project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backtesting import BacktestStrategy


def test_backtest_strategy(backtest_data):

    Logger.info(f"Runing test {str(backtest_data['name']).split('/')[2]}")
    # Extract the parameters from the fixture
    data = backtest_data["data"]
    tp_percent = backtest_data["tp_percent"]
    sl_percent = backtest_data["sl_percent"]
    leverage = backtest_data["leverage"]
    initial_margin = backtest_data["initial_margin"]

    # Initialize your strategy with the parameters
    strategy = BacktestStrategy(
        data=data,
        tp_percent=tp_percent,
        sl_percent=sl_percent,
        leverage=leverage,
        initial_margin=initial_margin,
    )

    # Run backtest
    strategy.run_backtest()

    # Add assertions to validate the backtest
    total_profit_loss = strategy.calculate_total_profit_loss()

    assert (
        total_profit_loss != 0
    ), f"Expected profit/loss > 0 but got {total_profit_loss}"
