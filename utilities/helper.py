import os
import shutil
import pandas as pd
from datetime import timedelta


def get_data(symbol, timestamp, year, month):
    # Get the absolute path of the parent directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)

    # Construct the path to the 'data' directory
    data_directory = os.path.join(parent_directory, "data")
    timestamp_directory = os.path.join(data_directory, timestamp)

    # Create the file path
    csv_filename = f"{symbol}-{timestamp}-{year}-{month}.csv"
    csv_path = os.path.join(timestamp_directory, csv_filename)

    return csv_path


def get_zip_files_path(symbol, month, timestamp):
    # Get the absolute path of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(script_directory, "zip_files")
    symbol_directory = os.path.join(data_directory, symbol)
    path = f"{month}-{timestamp}"
    month_directory = os.path.join(symbol_directory, path)
    return month_directory


def move_downloaded_file_to_required_folder(file_path: str, symbol):
    # Get the absolute path of the current script (located under 'utilities')
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Define the 'data' directory which is assumed to be in the parent directory of 'utilities'
    parent_directory = os.path.dirname(script_directory)

    # Get the current path of the file (assuming 'file_path' is relative to 'utilities')
    csv_file_current_path = os.path.join(parent_directory, file_path)

    # get data folder
    data_directory = os.path.join(parent_directory, "data")

    # Define the timestamp directory within 'data'
    timestamp_directory = os.path.join(data_directory, file_path.split("-")[1])

    # Ensure the timestamp directory exists
    os.makedirs(timestamp_directory, exist_ok=True)

    # Create the destination file path
    csv_filename = f"{symbol}-{file_path.split('-')[1]}-{file_path.split('-')[2]}-{file_path.split('-')[3]}"
    required_path = os.path.join(timestamp_directory, csv_filename)

    # Move the file to the required folder
    if os.path.exists(csv_file_current_path):
        shutil.move(csv_file_current_path, required_path)
        print(f"File moved to: {required_path}")
    else:
        print(f"Source file does not exist: {csv_file_current_path}")


def clean_and_save_data(file_path: str, start_date: str, end_date: str):
    # Load the data
    df = pd.read_csv(file_path)

    # Convert the open_time from Unix timestamp in milliseconds to a readable datetime format
    df["open_time_converted"] = pd.to_datetime(df["open_time"], unit="ms")

    # Convert start and end dates to datetime objects
    start_date = pd.to_datetime(start_date, format="%d/%m/%Y")
    end_date = pd.to_datetime(end_date, format="%d/%m/%Y")

    # Get the day before end_date
    day_before_end_date = end_date - timedelta(days=1)

    # Filter the DataFrame to only include data within the date range
    df_filtered = df[
        (df["open_time_converted"] >= start_date)
        & (df["open_time_converted"] < day_before_end_date)
    ]

    # Drop the conversion column (optional)
    df_filtered = df_filtered.drop(columns=["open_time_converted"])

    # Save the cleaned data back to the CSV
    df_filtered.to_csv(file_path, index=False)
    print("Cleaning data ...")
    print(f"Data saved to {file_path} with {len(df_filtered)} rows.")

    return file_path
