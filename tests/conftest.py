from pathlib import Path
import pytest
import yaml
import pandas as pd
import logging as Logger


@pytest.fixture(
    scope="module",
    params=yaml.safe_load(Path("tests/csv_config.yaml").read_text())["test_cases"],
)
def backtest_data(request):
    Logger.info("Extracting data ....")
    # Construct full path from relative path
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / request.param["csv_path"]
    data = pd.read_csv(csv_path)
    return {
        "name": request.param["csv_path"],
        "data": data,
        "tp_percent": request.param["tp_percent"],
        "sl_percent": request.param["sl_percent"],
        "leverage": request.param["leverage"],
        "initial_margin": request.param["initial_margin"],
    }
