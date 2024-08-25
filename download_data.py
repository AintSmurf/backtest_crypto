import requests
import time
import pandas as pd
from helper import move_downloaded_file_to_required_folder, clean_and_save_data


def get_historical_candles(symbol, interval, start_str, end_str):
    # real futures api not testnet if u wanna retrive testnet data use https://testnet.binancefuture.com
    base_url = "https://fapi.binance.com"
    endpoint = "/fapi/v1/klines"
    url = base_url + endpoint

    start_ts = int(time.mktime(time.strptime(start_str, "%d/%m/%Y")) * 1000)
    end_ts = int(time.mktime(time.strptime(end_str, "%d/%m/%Y")) * 1000)

    all_data = []

    while start_ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ts,
            "endTime": end_ts,
            "limit": 500,  # Maximum limit 1500
        }

        response = requests.get(url, params=params)
        data = response.json()

        if not data:
            break

        all_data += data

        # Move the start time to the last timestamp retrieved + 1ms to avoid overlap
        start_ts = data[-1][6] + 1

        # Sleep to avoid hitting rate limits
        time.sleep(1)

    # Convert data to DataFrame for easier handling
    df = pd.DataFrame(
        all_data,
        columns=[
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
        ],
    )
    # Save DataFrame to CSV
    start_date_obj = time.strptime(start_str, "%d/%m/%Y")
    year = start_date_obj.tm_year
    month = time.strftime("%B", start_date_obj)

    filename = f"{symbol}-{interval}-{year}-{month:02}.csv"
    df.to_csv(filename, index=False)

    print(f"Data saved to {filename} with {len(df)} rows.")
    return filename


if __name__ == "__main__":
    # Example usage
    symbol = "ADAUSDT"
    interval = "1m"
    start_str = "01/07/2024"
    end_str = "02/08/2024"
    # retrive data from binance api
    file_path = get_historical_candles(symbol, interval, start_str, end_str)

    # Clean the data
    cleaned_file_path = clean_and_save_data(file_path, start_str, end_str)

    # Move the cleaned file to the required folder
    move_downloaded_file_to_required_folder(cleaned_file_path, symbol)


# to check if downloaded data is legit with excel
# =(((A2/1000)/60)/60)/24 + DATE(1970,1,1)
