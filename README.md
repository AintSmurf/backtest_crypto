# Crypto Trading Backtesting Bot

## Overview
The Crypto Trading Backtesting Bot is a Python-based tool designed to backtest trading strategies using historical market data from Binance. The bot can download historical candlestick data, process it, and apply trading strategies to evaluate their performance. The results are saved in a CSV file, and key metrics like win rate and total profit/loss are calculated and displayed.

# Table of Contents
* [Features](#features)
* [Requirements](#requirements)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Data Management](#data-management)

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
# Example: Download 15-minute interval data for ETHUSDT from June 2024
get_historical_candles("ETHUSDT", "15m", "01/06/2024", "30/06/2024") 
```
* The downloaded data will be saved in the format SYMBOL-INTERVAL-YEAR-MONTH.csv, e.g., ETHUSDT-15m-2024-june.csv
```bash
python download_data.py 
```
5) **Organize Your Data:**
Move the downloaded CSV file to the appropriate folder:
* For 15-minute interval data, move the file to data/15m/
* For 30-minute interval data, move the file to data/30m/
etc ...

# Usage
* To perform a backtest, modify and run the app.py script:
```bash
# Example:
if __name__ == "__main__":
    csv_path = get_data(symbol="ETHUSDT", timestamp="15m", year=2024, month="june")
    df_updated = process_data(csv_path)

    # Initialize and run the backtest
    strategy = BacktestStrategy(df_updated, tp_percent=5, sl_percent=2.5, leverage=1)
    result = strategy.run_backtest("backtest_results.csv")

    # Calculate win rate
    win_rate = strategy.calculate_win_rate()
    print(f"Win Rate: {win_rate:.2f}%")

    # Calculate total profit/loss based on $100 initial investment
    initial_investment = 100
    total_profit_loss = strategy.calculate_total_profit_loss(initial_investment)
    print(f"Total Profit/Loss from {initial_investment} initial investment: ${total_profit_loss:.2f}")

    # Plot results
    strategy.plot_results()
```
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