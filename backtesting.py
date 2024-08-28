import pandas as pd
import ta
import matplotlib.pyplot as plt
from typing import Optional, Dict


class BacktestStrategy:
    def __init__(
        self,
        data,
        tp_percent: int,
        sl_percent: int,
        leverage: int,
        initial_margin: int,
    ):
        self.csv_path = getattr(data, "csv_path", "Unknown")
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

    def calculate_indicators(
        self,
        EMA_DAYS: Optional[int] = None,
        MACD_DAYS: Optional[Dict[str, int]] = None,
        RSI_DAYS: Optional[int] = None,
    ):
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

    def calculate_liquidation(self, buy_price: int, side: str):
        liquidation_price = 0
        if side == "Long":
            liquidation_price = buy_price * (
                1
                - (self.initial_margin * (1 - self.maintenance_margin))
                / (self.initial_margin * self.leverage)
            )
        elif side == "Short":
            liquidation_price = buy_price * (
                1
                + (self.initial_margin * (1 - self.maintenance_margin))
                / (self.initial_margin * self.leverage)
            )
        return liquidation_price

    def run_backtest(
        self,
        EMA_DAYS: Optional[int] = None,
        MACD_DAYS: Optional[Dict[str, int]] = None,
        RSI_DAYS: Optional[int] = None,
    ):
        if EMA_DAYS or MACD_DAYS or RSI_DAYS:
            self.calculate_indicators(EMA_DAYS, MACD_DAYS, RSI_DAYS)

        self.data["Position"] = 0  # to filter later to check results
        self.data["Trade_Result"] = 0.0  # To store profit or loss for each trade
        self.data["Trade_Type"] = None  # To store type of trade ('buy' or 'sell')
        self.data["side"] = None  # to check if its long or short
        self.data["Liquidated"] = False  # Track liquidation
        buy_price = None
        current_side = None

        for i in range(1, len(self.data)):
            # Buy condition Long Position
            if (
                self.data["MACD"].iloc[i] > self.data["Signal_Line"].iloc[i]
                and self.data["MACD"].iloc[i] < 0
                and self.data["Signal_Line"].iloc[i] < 0
                and self.data["close"].iloc[i] < self.data["EMA"].iloc[i]
                and self.data["RSI"].iloc[i] < 30
                and buy_price is None  # Ensure no existing buy position
            ):
                self.data.loc[self.data.index[i], "Position"] = 1  # Enter Long
                buy_price = self.data["close"].iloc[i]  # Record buy price
                self.data.loc[self.data.index[i], "Trade_Type"] = "buy"
                self.data.loc[self.data.index[i], "side"] = "Long"
                current_side = "Long"

                # Calculate stop loss and take profit prices considering leverage
                stop_loss_price = buy_price * (1 - (self.sl_percent / self.leverage))
                take_profit_price = buy_price * (1 + (self.tp_percent / self.leverage))
                print(f"Bought at index {i}, price {buy_price} - Long")

            # Buy condition Short Position
            if (
                self.data["MACD"].iloc[i] < self.data["Signal_Line"].iloc[i]
                and self.data["MACD"].iloc[i] > 0
                and self.data["Signal_Line"].iloc[i] > 0
                and self.data["close"].iloc[i] > self.data["EMA"].iloc[i]
                and self.data["RSI"].iloc[i] > 70
                and buy_price is None  # Ensure no existing buy position
            ):
                self.data.loc[self.data.index[i], "Position"] = 1  # Enter Short
                buy_price = self.data["close"].iloc[i]  # Record sell price (entry)
                self.data.loc[self.data.index[i], "Trade_Type"] = "sell"
                self.data.loc[self.data.index[i], "side"] = "Short"
                current_side = "Short"

                # Calculate stop loss and take profit prices considering leverage
                stop_loss_price = buy_price * (
                    1 + (self.sl_percent / self.leverage)
                )  # Stop loss above entry for short
                take_profit_price = buy_price * (
                    1 - (self.tp_percent / self.leverage)
                )  # Take profit below entry for short
                print(f"Sold at index {i}, price {buy_price} - Short")

            if buy_price is not None:
                current_price = self.data["close"].iloc[i]
                # Calculate the liquidation price for Long and Short positions
                liquidation_price = self.calculate_liquidation(
                    buy_price, self.data.loc[self.data.index[i], "side"]
                )

                # Check liquidation condition
                if (
                    self.data.loc[self.data.index[i], "side"] == "Long"
                    and current_price <= liquidation_price
                ) or (
                    self.data.loc[self.data.index[i], "side"] == "Short"
                    and current_price >= liquidation_price
                ):
                    self.data.loc[self.data.index[i], "Liquidated"] = True
                    self.data.loc[self.data.index[i], "Position"] = -1
                    sell_price = current_price
                    # Calculate trade result assuming full margin loss
                    trade_result = (
                        (current_price - buy_price) / buy_price * self.leverage
                        if self.data.loc[self.data.index[i], "side"] == "Long"
                        else (buy_price - current_price) / buy_price * self.leverage
                    )
                    self.data.loc[self.data.index[i], "Trade_Result"] = trade_result
                    self.data.loc[self.data.index[i], "Trade_Type"] = "Liquidated"
                    buy_price = None  # Reset buy_price after liquidation
                    print(f"Liquidated at index {i}, price {sell_price}")

                # Otherwise, check for TP/SL
                elif (
                    (current_side == "Long" and current_price >= take_profit_price)
                    or (current_side == "Long" and current_price <= stop_loss_price)
                    or (current_side == "Short" and current_price <= take_profit_price)
                    or (current_side == "Short" and current_price >= stop_loss_price)
                ):
                    self.data.loc[self.data.index[i], "Position"] = -1  # Close position
                    sell_price = current_price
                    # Calculate trade result (percentage gain/loss)
                    trade_result = (
                        (buy_price - current_price) / buy_price * self.leverage
                        if self.data.loc[self.data.index[i], "side"] == "Short"
                        else (current_price - buy_price) / buy_price * self.leverage
                    )
                    self.data.loc[self.data.index[i], "Trade_Result"] = trade_result
                    if current_side == "Short":
                        self.data.loc[self.data.index[i], "Trade_Type"] = "buy"
                        self.data.loc[self.data.index[i], "side"] = "Short"
                    else:
                        self.data.loc[self.data.index[i], "Trade_Type"] = "sell"
                        self.data.loc[self.data.index[i], "side"] = "Long"
                    print(f"Closed at index {i}, price {sell_price}")
                    buy_price = None  # Reset buy_price after closing the position
                    stop_loss_price = None  # Reset stop loss
                    take_profit_price = None  # Reset Take profit
                    # Save the results to a new CSV file
        output_csv_path = f"backtest_results.csv"
        self.data.to_csv(output_csv_path, index=False)

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

        # Plot long position entries (buys)
        long_entries = self.data[
            (self.data["Position"] == 1) & (self.data["side"] == "Long")
        ]
        ax1.scatter(
            long_entries.index,
            long_entries["close"],
            color="brown",
            marker="^",
            label="Long Entry",
        )

        # Plot short position entries (sells)
        short_entries = self.data[
            (self.data["Position"] == 1) & (self.data["side"] == "Short")
        ]
        ax1.scatter(
            short_entries.index,
            short_entries["close"],
            color="purple",
            marker="v",
            label="Short Entry",
        )

        # Plot lost trades for Long positions (negative result is a loss for Long)
        lost_long_trades = self.data[
            (self.data["Trade_Result"] < 0) & (self.data["side"] == "Long")
        ]
        ax1.scatter(
            lost_long_trades.index,
            lost_long_trades["close"],
            color="red",
            marker="x",
            label="Lost Long Trades",
        )

        # Plot lost trades for Short positions (positive result is a loss for Short)
        lost_short_trades = self.data[
            (self.data["Trade_Result"] > 0) & (self.data["side"] == "Short")
        ]
        ax1.scatter(
            lost_short_trades.index,
            lost_short_trades["close"],
            color="red",
            marker="x",
            label="Lost Short Trades",
        )

        # Plot successful trades for Long positions (positive result is a win for Long)
        successful_long_trades = self.data[
            (self.data["Trade_Result"] > 0) & (self.data["side"] == "Long")
        ]
        ax1.scatter(
            successful_long_trades.index,
            successful_long_trades["close"],
            color="blue",
            marker="^",
            label="Successful Long Trades",
            edgecolor="black",  # Add an edge color for visibility
        )

        # Plot successful trades for Short positions (negative result is a win for Short)
        successful_short_trades = self.data[
            (self.data["Trade_Result"] < 0) & (self.data["side"] == "Short")
        ]
        ax1.scatter(
            successful_short_trades.index,
            successful_short_trades["close"],
            color="blue",
            marker="v",
            label="Successful Short Trades",
            edgecolor="black",  # Add an edge color for visibility
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
        total_return = self.data["Trade_Result"].sum()
        liquidated_trades = self.data[self.data["Liquidated"] == True]
        if not liquidated_trades.empty:
            print(f"You got liquidated at the following prices:")
            for idx, row in liquidated_trades.iterrows():
                print(f" - Price: {row['close']:.5f} at index {idx}")
            return 0
        return self.initial_margin + total_return
