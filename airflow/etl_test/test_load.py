import duckdb
import pandas as pd
from airflow.etl.load import load
from airflow.etl_test.utils import get_today_str

today_str = get_today_str()

def test_initial_load(tmp_path):
    """
    Test that the first load inserts all rows into weather_data.
    """

    # Create a temporary CSV
    csv_file = tmp_path / "weather.csv"
    df = pd.DataFrame({
        "time": [f"{today_str}T00:00", f"{today_str}T01:00"],
        "temperature_2m": [20.0, 21.5],
        "precipitation": [0.1, 0.0]
    })
    df.to_csv(csv_file, index=False)

    # Temporary DuckDB file
    db_file = tmp_path / "weather.duckdb"

    # Run load
    load(csv_file, db_file)

    con = duckdb.connect(db_file)
    result = con.execute("SELECT * FROM weather_data ORDER BY time").fetchall()

    assert len(result) == 2
    assert result[0][1] == 20.0
    assert result[0][2] == 0.1

def test_merge_updates_data_and_modified_date(tmp_path):
    """
    Test that MERGE updates data and modified_date when values change.
    """

    # Initial CSV
    csv_file = tmp_path / "weather.csv"
    df1 = pd.DataFrame({
        "time": [f"{today_str}T00:00"],
        "temperature_2m": [20.0],
        "precipitation": [0.1]
    })
    df1.to_csv(csv_file, index=False)

    # Temporary DuckDB file
    db_file = tmp_path / "weather.duckdb"

    # First load
    load(csv_file, db_file)

    con = duckdb.connect(db_file)
    row1 = con.execute(f"""
        SELECT creation_date, modified_date
        FROM weather_data
        WHERE time = '{today_str}T00:00'
    """).fetchone()

    creation_1, modified_1 = row1

    # Second CSV with updated values
    df2 = pd.DataFrame({
        "time": [f"{today_str}T00:00"],
        "temperature_2m": [22.0],   # changed
        "precipitation": [0.1]
    })
    df2.to_csv(csv_file, index=False)

    # Second load
    load(csv_file, db_file)

    row2 = con.execute(f"""
        SELECT temperature_2m, creation_date, modified_date
        FROM weather_data
        WHERE time = '{today_str}T00:00'
    """).fetchone()

    temp_2, creation_2, modified_2 = row2

    # Value updated
    assert temp_2 == 22.0
    # creation_date must NOT change
    assert creation_2 == creation_1
    # modified_date must change
    assert modified_2 != modified_1

def test_merge_updates_only_modified_date_when_identical(tmp_path):
    """
    Test that MERGE updates only modified_date when values are identical.
    """

    # Initial CSV
    csv_file = tmp_path / "weather.csv"
    df1 = pd.DataFrame({
        "time": [f"{today_str}T00:00"],
        "temperature_2m": [20.0],
        "precipitation": [0.1]
    })
    df1.to_csv(csv_file, index=False)

    # Temporary DuckDB file
    db_file = tmp_path / "weather.duckdb"

    # First load
    load(csv_file, db_file)

    con = duckdb.connect(db_file)
    row1 = con.execute(f"""
        SELECT temperature_2m, precipitation, creation_date, modified_date
        FROM weather_data
        WHERE time = '{today_str}T00:00'
    """).fetchone()

    temperature_1, precipitation_1, creation_1, modified_1 = row1

    # Second CSV identical
    df1.to_csv(csv_file, index=False)

    # Second load
    load(csv_file, db_file)

    row2 = con.execute(f"""
        SELECT temperature_2m, precipitation, creation_date, modified_date
        FROM weather_data
        WHERE time = '{today_str}T00:00'
    """).fetchone()

    temperature_2, precipitation_2, creation_2, modified_2 = row2

    # Change only in modified
    assert temperature_2 == temperature_1
    assert precipitation_2 == precipitation_1
    assert creation_2 == creation_1
    assert modified_2 != modified_1
