import pandas as pd
from helper import *
from backtesting import BacktestStrategy


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
    csv_path = get_data(symbol="ETHUSDT", timestamp="15m", year=2024, month="june")
    df_updated = process_data(csv_path)

    # Initialize and run the backtest
    strategy = BacktestStrategy(df_updated, tp_percent=5, sl_percent=2.5, leverage=1)

    # it will output the results with excel
    result = strategy.run_backtest("backtest_results.csv")

    # Calculate win rate
    win_rate = strategy.calculate_win_rate()
    print(f"Win Rate: {win_rate:.2f}%")

    # Calculate total profit/loss based on $100 initial investment
    initial_investment = 100
    total_profit_loss = strategy.calculate_total_profit_loss(initial_investment)
    print(
        f"Total Profit/Loss from {initial_investment} initial investment: ${total_profit_loss:.2f}"
    )
    # plot results
    strategy.plot_results()
