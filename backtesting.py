import pandas as pd
import ta
import matplotlib.pyplot as plt


class BacktestStrategy:
    def __init__(self, data, tp_percent, sl_percent, leverage):
        self.data = data
        self.tp_percent = tp_percent / 100  # Convert to decimal
        self.sl_percent = sl_percent / 100  # Convert to decimal
        self.leverage = leverage  # Leverage factor (e.g., 10 for 10x leverage)
        # Calculate EMA
        self.data["EMA_200"] = ta.trend.EMAIndicator(
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

    def run_backtest(self, output_csv_path):
        self.data["Position"] = 0
        self.data["Trade_Result"] = 0.0  # To store profit or loss for each trade
        self.data["Trade_Type"] = None  # To store type of trade ('buy' or 'sell')
        buy_price = None
        for i in range(1, len(self.data)):
            # Buy condition
            if (
                self.data["MACD"].iloc[i] > self.data["Signal_Line"].iloc[i]
                and self.data["MACD"].iloc[i] < 0
                and self.data["Signal_Line"].iloc[i] < 0
                and self.data["close"].iloc[i] < self.data["EMA_200"].iloc[i]
                and self.data["RSI"].iloc[i] < 30
                and buy_price is None  # Ensure no existing buy position
            ):
                self.data.loc[self.data.index[i], "Position"] = 1  # Buy
                buy_price = self.data["close"].iloc[i]  # Record buy price
                self.data.loc[self.data.index[i], "Trade_Type"] = "buy"

            # Check for TP and SL
            if buy_price is not None:
                current_price = self.data["close"].iloc[i]
                if current_price >= buy_price * (
                    1 + self.tp_percent
                ) or current_price <= buy_price * (  # TP condition
                    1 - self.sl_percent
                ):  # SL condition
                    self.data.loc[self.data.index[i], "Position"] = -1  # Sell
                    sell_price = current_price
                    # Calculate trade result (percentage gain/loss)
                    trade_result = (
                        (sell_price - buy_price) / buy_price
                    ) * self.leverage
                    self.data.loc[self.data.index[i], "Trade_Result"] = trade_result
                    self.data.loc[self.data.index[i], "Trade_Type"] = "sell"
                    buy_price = None  # Reset buy_price after selling

        # Save the results to a new CSV file
        self.data.to_csv(output_csv_path, index=False)
        return self.data

    def plot_results(self):
        # Plot MACD and Signal Line
        plt.plot(self.data.index, self.data["MACD"], label="MACD", color="blue")
        plt.plot(
            self.data.index, self.data["Signal_Line"], label="MACD Signal", color="red"
        )
        # add ema
        plt.plot(self.data.index, self.data["EMA_200"], label="EMA", color="yellow")

        # Plot RSI
        plt.plot(self.data.index, self.data["RSI"], label="RSI", color="orange")
        # Add horizontal line at 0 for MACD
        plt.axhline(y=0, color="gray", linestyle="--", label="0 Line")

        # Plot closing price
        plt.plot(
            self.data.index,
            self.data["close"],
            label="Close Price",
            color="green",
            alpha=0.5,
        )

        # Plot trades
        successful_trades = self.data[self.data["Trade_Result"] != 0.0]
        plt.scatter(
            successful_trades.index,
            successful_trades["close"],
            color="brown",
            marker="^",
            label="Trades",
        )
        # Plot successful trades
        successful_trades = self.data[self.data["Trade_Result"] > 0]
        plt.scatter(
            successful_trades.index,
            successful_trades["close"],
            color="blue",
            marker="^",
            label="Successful Trades",
        )

        plt.title("MACD, MACD Signal, RSI, Close Price, and Successful Trades")
        plt.legend()
        plt.show()

    def calculate_win_rate(self):
        trades = self.data[self.data["Trade_Result"] != 0.0]
        if len(trades) == 0:
            return 0
        wins = trades[trades["Trade_Result"] > 0]
        win_rate = len(wins) / len(trades) * 100
        return win_rate

    def calculate_total_profit_loss(self, initial_investment):
        total_return = (1 + self.data["Trade_Result"]).cumprod().iloc[-1]
        return initial_investment * total_return
