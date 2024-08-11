import os


def get_data(symbol, timestamp, year, month):
    # Get the absolute path of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(script_directory, "data")
    timestamp_directory = os.path.join(data_directory, timestamp)
    # Create the file path
    csv_filename = f"{symbol}-{timestamp}-{year}-{month}.csv"
    csv_path = os.path.join(timestamp_directory, csv_filename)
    return csv_path


def get_zipl_files_path(symbol, month, timestamp):
    # Get the absolute path of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(script_directory, "zip_files")
    symbol_directory = os.path.join(data_directory, symbol)
    path = f"{month}-{timestamp}"
    month_directory = os.path.join(symbol_directory, path)
    return month_directory
