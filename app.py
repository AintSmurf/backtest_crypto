import pandas as pd
from helper import *
from backtesting import BacktestStrategy
from web_socket_utility import WebSocketHandler
import time


def process_data(csv_path):
    column_titles = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "count",
        "taker_buy_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    try:
        df = pd.read_csv(csv_path)
        # Drop the unnamed column if it exists
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        print(
            f"DataFrame loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns."
        )
        df.columns = column_titles
        # Convert Unix timestamps (in milliseconds) to datetime
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
        return df

    except FileNotFoundError:
        print(f"File not found: {csv_path}")
    except pd.errors.EmptyDataError:
        print("No data found in the file.")
    except pd.errors.ParserError:
        print("Error parsing the file.")


if __name__ == "__main__":
    # Initialize the WebSocketHandler only once
    ws_handler = WebSocketHandler()

    # Subscribe to the desired symbol and interval
    ws_handler.subscribe("btcusdt", interval="1m")
    try:
        while True:
            time.sleep(1)
            ws_handler.data_pulling_loop()
    except KeyboardInterrupt:
        ws_handler.stop()
        print("WebSocket handler stopped.")
    # csv_path = get_data(symbol="BTCUSDT", timestamp="5m", year=2024, month="july")
    # df_updated = process_data(csv_path)
    # initial_investment = 100
    # # Initialize and run the backtest
    # strategy = BacktestStrategy(
    #     df_updated,
    #     tp_percent=10,
    #     sl_percent=2.5,
    #     leverage=5,
    #     initial_margin=initial_investment,
    # )

    # # it will output the results to csv file
    # strategy.run_backtest()

    # # Calculate win rate
    # win_rate = strategy.calculate_win_rate()
    # print(f"\nWin Rate: {win_rate:.2f}%\n")

    # # Calculate total profit/loss based on  initial investment
    # total_profit_loss = strategy.calculate_total_profit_loss()
    # print(
    #     f"Total Profit/Loss from {initial_investment} initial investment: ${total_profit_loss:.2f}"
    # )
    # # plot results
    # strategy.plot_results()
