import pandas as pd
import ta
import matplotlib.pyplot as plt
from typing import Optional, Dict


class BacktestStrategy:
    def __init__(
        self, data, tp_percent: int, sl_percent: int, leverage: int, initial_margin: int
    ):
        self.data = data
        self.tp_percent = tp_percent / 100  # Convert to decimal
        self.sl_percent = sl_percent / 100  # Convert to decimal
        self.leverage = leverage  # Leverage factor (e.g., 10 for 10x leverage)
        self.initial_margin = initial_margin  # Initial margin allocated per trade
        self.maintenance_margin = 0.8  # Liquidation if margin falls below 80%
        # Calculate EMA
        self.data["EMA"] = ta.trend.EMAIndicator(
            self.data["close"], window=200
        ).ema_indicator()
        # Calculate MACD
        macd = ta.trend.MACD(self.data["close"])
        self.data["MACD"] = macd.macd()
        self.data["Signal_Line"] = macd.macd_signal()
        # Calculate RSI
        self.data["RSI"] = ta.momentum.RSIIndicator(self.data["close"], window=14).rsi()
        # Drop rows with NaN values
        self.data.dropna(inplace=True)

    def run_backtest(
        self,
        EMA_DAYS: Optional[int] = None,
        MACD_DAYS: Optional[Dict[str, int]] = None,
        RSI_DAYS: Optional[int] = None,
    ):
        # Example MACD_DAYS dict format
        macd_example = {
            "window_fast": 12,
            "window_slow": 26,
            "window_sign": 9,
        }
        if MACD_DAYS is not None:
            # Check if the MACD_DAYS format is correct
            if not isinstance(MACD_DAYS, dict) or not all(
                key in MACD_DAYS
                for key in ["window_fast", "window_slow", "window_sign"]
            ):
                raise ValueError(
                    f"MACD_DAYS should be a dictionary in the following format:\n {macd_example}"
                )
        if EMA_DAYS or MACD_DAYS or RSI_DAYS:
            self.data["EMA"] = ta.trend.EMAIndicator(
                self.data["close"], window=EMA_DAYS if EMA_DAYS else 200
            ).ema_indicator()
            self.data["RSI"] = ta.momentum.RSIIndicator(
                self.data["close"], window=RSI_DAYS if RSI_DAYS else 14
            ).rsi()
            if MACD_DAYS:
                macd = ta.trend.MACD(
                    self.data["close"],
                    window_fast=MACD_DAYS.get("window_fast", 12),
                    window_slow=MACD_DAYS.get("window_slow", 26),
                    window_sign=MACD_DAYS.get("window_sign", 9),
                )
                self.data["MACD"] = macd.macd()
                self.data["Signal_Line"] = macd.macd_signal()
        self.data["Position"] = 0
        self.data["Trade_Result"] = 0.0  # To store profit or loss for each trade
        self.data["Trade_Type"] = None  # To store type of trade ('buy' or 'sell')
        self.data["side"] = None  # to check if its long or short
        self.data["Liquidated"] = False  # Track liquidation
        buy_price = None

        for i in range(1, len(self.data)):
            # Buy condition
            if (
                self.data["MACD"].iloc[i] > self.data["Signal_Line"].iloc[i]
                and self.data["MACD"].iloc[i] < 0
                and self.data["Signal_Line"].iloc[i] < 0
                and self.data["close"].iloc[i] < self.data["EMA"].iloc[i]
                and self.data["RSI"].iloc[i] < 30
                and buy_price is None  # Ensure no existing buy position
            ):
                self.data.loc[self.data.index[i], "Position"] = 1  # Buy
                buy_price = self.data["close"].iloc[i]  # Record buy price
                self.data.loc[self.data.index[i], "Trade_Type"] = "buy"
                self.data.loc[self.data.index[i], "side"] = "Long"
                print(f"Bought at index {i}, price {buy_price}")

            if buy_price is not None:
                current_price = self.data["close"].iloc[i]

                # Calculate the liquidation price
                position_size = self.initial_margin * self.leverage
                liquidation_price = buy_price * (
                    1
                    - (self.initial_margin * (1 - self.maintenance_margin))
                    / position_size
                )

                # Check liquidation condition
                if current_price <= liquidation_price:
                    self.data.loc[self.data.index[i], "Liquidated"] = True
                    self.data.loc[self.data.index[i], "Position"] = -1
                    sell_price = current_price
                    # Calculate trade result assuming full margin loss
                    trade_result = (
                        (current_price - buy_price) / buy_price * self.leverage
                    )
                    self.data.loc[self.data.index[i], "Trade_Result"] = trade_result
                    self.data.loc[self.data.index[i], "Trade_Type"] = "Liquidated"
                    buy_price = None  # Reset buy_price after liquidation
                    print(f"Liquidated at index {i}, price {sell_price}")

                # Otherwise, check for TP/SL
                elif current_price >= buy_price * (
                    1 + self.tp_percent
                ) or current_price <= buy_price * (1 - self.sl_percent):
                    self.data.loc[self.data.index[i], "Position"] = -1  # Sell
                    sell_price = current_price
                    # Calculate trade result (percentage gain/loss)
                    trade_result = (
                        (current_price - buy_price) / buy_price * self.leverage
                    )
                    self.data.loc[self.data.index[i], "Trade_Result"] = trade_result
                    self.data.loc[self.data.index[i], "Trade_Type"] = "sell"
                    print(f"Sold at index {i}, price {sell_price}")
                    buy_price = None  # Reset buy_price after selling

        # Save the results to a new CSV file
        output_csv_path = "backtest_results.csv"
        self.data.to_csv(output_csv_path, index=False)
        return self.data

    def plot_results(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

        # First subplot: Close Price, EMA, Buy/Sell trades
        ax1.plot(
            self.data.index,
            self.data["close"],
            label="Close Price",
            color="green",
            alpha=0.7,
        )
        ax1.plot(self.data.index, self.data["EMA"], label="EMA", color="yellow")

        buying_position = self.data[self.data["Trade_Type"] == "buy"]
        ax1.scatter(
            buying_position.index,
            buying_position["close"],
            color="brown",
            marker="^",
            label="Buy Trades",
        )
        # Annotate buy price
        for idx, row in buying_position.iterrows():
            ax1.text(
                idx,
                row["close"],
                f'{row["close"]:.2f}',
                color="brown",
                fontsize=14,
                verticalalignment="bottom",
            )

        lost_trades = self.data[self.data["Trade_Result"] < 0.0]
        ax1.scatter(
            lost_trades.index,
            lost_trades["close"],
            color="red",
            marker="v",
            label="Lost Trades",
        )

        successful_trades = self.data[self.data["Trade_Result"] > 0]
        ax1.scatter(
            successful_trades.index,
            successful_trades["close"],
            color="blue",
            marker="^",
            label="Successful Trades",
        )

        # Identify and annotate liquidation events
        liquidated_trades = self.data[self.data["Liquidated"] == True]
        for idx, row in liquidated_trades.iterrows():
            ax1.text(
                idx,
                row["close"],
                f'Liqudation {row["close"]:.2f}',
                color="black",
                fontsize=14,
                verticalalignment="bottom",
                horizontalalignment="left",
            )
        ax1.set_ylabel("Price")
        ax1.legend(loc="upper left")
        ax1.set_title("Close Price, EMA, and Trades")

        # Second subplot: MACD and Signal Line
        ax2.plot(self.data.index, self.data["MACD"], label="MACD", color="blue")
        ax2.plot(
            self.data.index, self.data["Signal_Line"], label="MACD Signal", color="red"
        )
        ax2.axhline(y=0, color="gray", linestyle="--", label="0 Line")

        ax2.set_ylabel("MACD")
        ax2.legend(loc="upper left")
        ax2.set_title("MACD and MACD Signal Line")

        # Third subplot: RSI
        ax3.plot(
            self.data.index, self.data["RSI"], label="RSI", color="orange", alpha=0.7
        )
        ax3.axhline(y=70, color="red", linestyle="--", alpha=0.5)
        ax3.axhline(y=30, color="green", linestyle="--", alpha=0.5)

        ax3.set_ylabel("RSI")
        ax3.set_xlabel("Time")
        ax3.legend(loc="upper left")
        ax3.set_title("RSI")

        plt.tight_layout()
        plt.show()

    def calculate_win_rate(self):
        trades = self.data[self.data["Trade_Result"] != 0.0]
        if len(trades) == 0:
            return 0
        wins = trades[trades["Trade_Result"] > 0]
        win_rate = len(wins) / len(trades) * 100
        return win_rate

    def calculate_total_profit_loss(self):
        total_return = self.data["Trade_Result"].sum() * 10
        liquidated_trades = self.data[self.data["Liquidated"] == True]
        if not liquidated_trades.empty:
            print(f"You got liquidated at the following prices:")
            for idx, row in liquidated_trades.iterrows():
                print(f" - Price: {row['close']:.2f} at index {idx}")
            return 0
        return self.initial_margin + total_return
