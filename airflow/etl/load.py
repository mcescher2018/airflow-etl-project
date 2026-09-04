import sys
import os
import duckdb
import pandas as pd

def preview_table(con, table_name, limit=5):
    """
    Print row count and first N rows of a DuckDB table.
    """
    print(f"\n=== Preview of table: {table_name} ===")

    # Row count
    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
    print(f"Row count: {row_count}")

    # First rows
    df_preview = con.execute(
        f"SELECT * FROM {table_name} LIMIT {limit};"
    ).fetchdf()

    print(df_preview.to_string(index=False))


def load(csv_path, db_path):
    """
    Load the CSV into DuckDB using a proper UPSERT strategy with MERGE.
    Uniform error handling:
    - CSV must exist
    - CSV must not be empty
    - CSV must contain required columns
    """

    # Check CSV exists
    if not os.path.exists(csv_path):
        msg = f"CSV file not found: {csv_path}"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    # Check CSV not empty
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        msg = f"Failed to read CSV '{csv_path}': {e}"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    if df.empty:
        msg = f"CSV '{csv_path}' is empty"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    # Check required columns
    required_columns = ["time", "temperature_2m", "precipitation"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        msg = f"Missing required columns in CSV: {missing}"
        print(f"[ERROR] {msg}. Available columns: {list(df.columns)}")
        raise ValueError(msg)

    # Connect to DuckDB
    try:
        con = duckdb.connect(db_path)
    except Exception as e:
        msg = f"Failed to connect to DuckDB at '{db_path}': {e}"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    # Final table with audit fields
    con.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            time TIMESTAMP PRIMARY KEY,
            temperature_2m DOUBLE,
            precipitation DOUBLE,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Staging table (no audit fields)
    con.execute("""
        CREATE TABLE IF NOT EXISTS weather_staging (
            time TIMESTAMP,
            temperature_2m DOUBLE,
            precipitation DOUBLE
        );
    """)

    # Clear staging
    con.execute("DELETE FROM weather_staging;")

    # Load CSV into staging
    con.execute(f"""
        INSERT INTO weather_staging
        SELECT * FROM read_csv_auto('{csv_path}');
    """)

    # MERGE = real UPSERT
    con.execute("""
        MERGE INTO weather_data AS target
        USING weather_staging AS source
        ON target.time = source.time

        WHEN MATCHED THEN
            UPDATE SET
                temperature_2m = source.temperature_2m,
                precipitation = source.precipitation,
                modified_date = CURRENT_TIMESTAMP

        WHEN NOT MATCHED THEN
            INSERT (time, temperature_2m, precipitation, creation_date, modified_date)
            VALUES (
                source.time,
                source.temperature_2m,
                source.precipitation,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            );
    """)

    print(f"UPSERT completed with MERGE. Database updated at: {db_path}")

    preview_table(con, "weather_staging")
    preview_table(con, "weather_data")

    return db_path


if __name__ == "__main__":
    """
        Standalone debug mode:
        Run: python load.py ../data/weather_staging.csv ../data/weather.duckdb
    """

    if len(sys.argv) != 3:
        print("Usage: python load.py <csv_path> <db_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    db_path = sys.argv[2]
    load(csv_path, db_path)