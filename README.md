# Crypto Trading Backtesting Bot

## Overview
The Crypto Trading Backtesting Bot is a Python-based tool designed to backtest trading strategies using historical market data from Binance. The bot can download historical candlestick data, process it, and apply trading strategies to evaluate their performance. The results are saved in a CSV file, and key metrics like win rate and total profit/loss are calculated and displayed.

# Table of Contents
* [Features](#features)
* [Requirements](#requirements)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Supported Indicators](#Supported-Indicators)
* [Limitations](#Limitations)
* [Future Enhancements](#Future-Enhancements)
* [Project Structure](#Project-Structure)


# Features
* **Historical Data Download**: Download historical candlestick data for any trading pair and timeframe from Binance.
* **Backtesting**: Apply trading strategies to historical data to evaluate performance.
* **Result Analysis**: Calculate win rate and total profit/loss from backtesting results.
* **Data Export**: Save processed data and results to CSV files for further analysis.

# Requirements
* Python 3.x
* `requests` library
* `pandas` library
* `matplotlib` library (for plotting backtest results)

# Getting Started
1) **Clone this repository to your local machine:**
```bash
git clone https://github.com/your-repository/crypto-backtesting-bot.git
```
2) **create virtual environment:(not required)**
```bash
python -m venv venv
```
3) **Install Dependencies:**
Navigate to the project directory and install the required Python packages:
```bash
pip install -r requirements.txt
```
4) **Download Historical Data:**
```bash
# Example: Download 15-minute interval data for ETHUSDT for June 2024
get_historical_candles("ETHUSDT", "15m", "01/06/2024", "02/07/2024") 
```
* The downloaded data will be automatically saved in the correct folder under data/INTERVAL/, with a filename format of SYMBOL-INTERVAL-YEAR-MONTH.csv, e.g., ETHUSDT-15m-2024-June.csv
```bash
python download_data.py 
```
5) **Automated Data Organization:**
When you run the download script, the data will automatically be saved in the appropriate folder based on the interval. For example:
* For 5-minute interval data, it will be saved under data/5m/
* For 1-hour interval data, it will be saved under data/1h/
* And so on..
* To download data that spans across months, for example from 01/08/2024 to the end of August, you need to provide the exact start date and use end_date + 2 (e.g., 02/09/2024) as the end date to ensure you capture the entire month.

# Usage
* To perform a backtest, modify and run the app.py script:
```bash
# Example:
if __name__ == "__main__":
    csv_path = get_data(symbol="ADAUSDT", timestamp="5m", year=2024, month="july")
    df_updated = process_data(csv_path)
    initial_investment = 100
    # Initialize and run the backtest
    strategy = BacktestStrategy(df_updated, tp_percent=5, sl_percent=2.5, leverage=5, initial_margin=initial_investment)

    # it will output the results to csv file
    strategy.run_backtest()

    # Calculate win rate
    win_rate = strategy.calculate_win_rate()
    print(f"\nWin Rate: {win_rate:.2f}%\n")

    # Calculate total profit/loss based on  initial investment
    total_profit_loss = strategy.calculate_total_profit_loss()
    print(f"Total Profit/Loss from {initial_investment} initial investment: ${total_profit_loss:.2f}")
    
    # plot results
    strategy.plot_results()
```
* Running app.py will automatically produce a CSV{backtest_results.csv} file with the results of the backtest.

# Supported Indicators
* Currently, the backtest supports the following technical indicators:
    * Exponential Moving Average (EMA)
    * Moving Average Convergence Divergence (MACD)
    * Relative Strength Index (RSI)
* You can modify the parameters for these indicators by passing them as arguments to the strategy.run_backtest() method:
```bash
# Typing:
def run_backtest(
    EMA_DAYS: int | None = None,
    MACD_DAYS: Dict[str, int] | None = None,
    RSI_DAYS: int | None = None
)
```
* For example, to adjust the EMA period and the MACD settings, you might use:
```bash
# Example:
strategy.run_backtest(EMA_DAYS=50, MACD_DAYS={"window_fast": 12, "window_slow": 26, "window_sign": 9})
```
# Limitations
* **Trade Types**: Currently, the backtest only supports isolated trades and long positions. Support for cross-margin trades and short positions will be added in future updates.
* **Indicators**: The bot supports only three indicators (EMA, MACD, RSI). More indicators will be added in future versions.

# Future Enhancements
* **Cross-Margin Trades**: Future updates will include support for cross-margin trades.
* **Short Trades**: The ability to backtest short trades will be added.
* **Additional Indicators**: Plans to include additional technical indicators such as Bollinger Bands, Stochastic RSI, and others.

# Project Structure
```plaintext
    ├── data/
    │   ├───15m/
    │   │    └── ETHUSDT-15m-2024-june.csv
    │   │    └── BTCSDT-15m-2024-june.csv
    │   │
    │   ├───1d/
    │   ├───1h/
    │   ├───30m/
    │   └───4h/
    ├── helper.py
    ├── backtesting.py
    ├── download_data.py
    ├── app.py
    ├── README.md
    └── requirements.txt

```