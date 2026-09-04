import pandas as pd
from airflow.etl.transform import transform
from airflow.etl_test.utils import get_today_str

today_str = get_today_str()

def test_transform_creates_csv(tmp_path):
    """
    Test that transform() creates a CSV with the expected content using pandas.
    """

    data = {
        "hourly": {
            "time": [f"{today_str}T00:00", f"{today_str}T01:00"],
            "temperature_2m": [20.0, 21.5],
            "precipitation": [0.1, 0.0]
        }
    }

    # Build filename dynamically from tmp_path
    tmp_filename = tmp_path / "weather.csv"

    # Run transform
    result = transform(data, tmp_filename)

    # The function returns None (by design)
    assert result is None

    # Verify the CSV exists
    assert tmp_filename.exists()

    # Load CSV with pandas
    df = pd.read_csv(tmp_filename)

    # Check columns
    assert list(df.columns) == ["time", "temperature_2m", "precipitation"]

    # Check row count
    assert len(df) == 2

    # Check values
    assert df.loc[0, "time"] == f"{today_str}T00:00"
    assert df.loc[0, "temperature_2m"] == 20.0
    assert df.loc[0, "precipitation"] == 0.1

    assert df.loc[1, "time"] == f"{today_str}T01:00"
    assert df.loc[1, "temperature_2m"] == 21.5
    assert df.loc[1, "precipitation"] == 0.0

def test_transform_missing_field(tmp_path):
    """
    Test that transform() fails when required fields are missing.
    """

    data = {
        "hourly": {
            "time": [f"{today_str}T00:00"],
            "temperature_2m": [20.0]
            # precipitation missing
        }
    }

    tmp_filename = tmp_path / "weather.csv"

    try:
        transform(data, tmp_filename)
        assert False, "Expected KeyError for missing field"
    except ValueError:
        pass
