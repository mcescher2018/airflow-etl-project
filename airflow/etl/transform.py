import sys
import json
import pandas as pd

def transform(data, filename, expected_granularity="hourly"):
    """
    Transform the Open-Meteo JSON payload into a CSV file using pandas.
    Requires the expected granularity (default: 'hourly') to exist.
    """

    # Ensure expected granularity exists
    if expected_granularity not in data:
        msg = f"{expected_granularity} tag must exist in input data"
        print(f"[ERROR] {msg}. Available keys: {list(data.keys())}")
        raise ValueError(msg)

    gran = data[expected_granularity]

    # Ensure granularity is not empty
    if not gran:
        msg = f"{expected_granularity} tag exists but is empty"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    # Ensure required fields exist
    required_fields = ["time", "temperature_2m", "precipitation"]
    missing = [field for field in required_fields if field not in gran]

    if missing:
        msg = f"Missing required fields in '{expected_granularity}': {missing}"
        print(f"[ERROR] {msg}. Available fields: {list(gran.keys())}")
        raise ValueError(msg)

    # Build DataFrame
    try:
        df = pd.DataFrame({
            "time": gran["time"],
            "temperature_2m": gran["temperature_2m"],
            "precipitation": gran["precipitation"]
        })
    except Exception as e:
        msg = f"Failed to build DataFrame for '{expected_granularity}': {e}"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    # Ensure DataFrame is not empty
    if df.empty:
        msg = f"DataFrame for '{expected_granularity}' is empty"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    # Preview
    print(f"Saving CSV to: {filename}")
    print("File first lines preview:")
    print(df.head().to_csv(index=False))

    # Save CSV
    try:
        df.to_csv(filename, index=False)
    except Exception as e:
        msg = f"Failed to save CSV to '{filename}': {e}"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    return None


if __name__ == "__main__":
    """
    Standalone debug mode:
    Run: python transform.py input.json output.csv
    """

    if len(sys.argv) != 3:
        print("Usage: python transform.py <input_json> <output_csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r") as f:
        data = json.load(f)

    result = transform(data, output_file)