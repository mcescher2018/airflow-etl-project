import sys
import pandas as pd
import requests

def extract(ds, full_url, expected_granularity="hourly"):
    """
    Extract JSON data from full_url.
    Requires the expected granularity (default: 'hourly') to exist in the API response.
    """

    print(f"Call API for ds={ds}: {full_url}")

    response = requests.get(full_url)
    response.raise_for_status()

    data = response.json()

    # Ensure expected granularity exists
    if expected_granularity not in data:
        msg = f"{expected_granularity} tag must exist in API response"
        print(f"[ERROR] {msg}. Available keys: {list(data.keys())}")
        raise ValueError(msg)

    gran = data[expected_granularity]

    # Check if granularity is empty
    if not gran:
        msg = f"{expected_granularity} tag exists but is empty"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    # Preview DataFrame
    try:
        df = pd.DataFrame(gran)
        print(f"[INFO] {expected_granularity.capitalize()} DataFrame preview:")
        print(df.head())
    except Exception as e:
        msg = f"Failed to convert '{expected_granularity}' to DataFrame: {e}"
        print(f"[ERROR] {msg}")
        raise ValueError(msg)

    return data

if __name__ == "__main__":
    """
    Standalone debug mode:
    Usage:
        python extract.py <date> <full_url>

    Note:
        The API response MUST contain the expected granularity (default: 'hourly').
    """

    if len(sys.argv) != 3:
        print("Usage: python extract.py <date> <full_url>")
        sys.exit(1)

    ds = sys.argv[1]
    full_url = sys.argv[2]

    extract(ds, full_url)
