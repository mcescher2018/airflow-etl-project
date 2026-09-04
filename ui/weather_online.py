import duckdb
import pandas as pd
import streamlit as st
import numpy as np

# Connect to DuckDB
con = duckdb.connect("../airflow/data/weather.duckdb")

# ============================================
# Title & Latest Update info
# ============================================

# Retrieve the timestamp of the latest ETL update
last_update = con.execute("""
    SELECT MAX(modified_date) FROM weather_data
""").fetchone()[0]

st.title("Weather Data Viewer")
st.subheader(f"Latest update: {last_update}")

# ============================================
# Latest Snapshot
# ============================================

# Load the full 192-hour snapshot corresponding to the latest update
# (current day + 7-day hourly forecast)
df = con.execute(f"""
    SELECT *
    FROM weather_data
    WHERE modified_date = '{last_update}'
    ORDER BY time
""").fetchdf()

# Display the latest snapshot (not the historical dataset)
st.subheader("Latest Snapshot (192-hour window)")
st.dataframe(df, use_container_width=True)

# ============================================
# Basic stats
# ============================================

# Basic summary statistics for the latest snapshot
st.subheader("Summary Statistics")
st.write(df[["temperature_2m", "precipitation"]].describe())

# ============================================
# Temperature Trend Forecasting
# ============================================

# Temperature trend using a simple linear regression
st.subheader("Temperature Trend Forecasting (Linear Regression)")

# Convert time to a numeric index for regression
df["time_index"] = np.arange(len(df))

# Fit a simple linear regression model
coeffs = np.polyfit(df["time_index"], df["temperature_2m"], 1)
trend_line = coeffs[0] * df["time_index"] + coeffs[1]

trend_df = pd.DataFrame({
    "time": df["time"],
    "temperature_2m": df["temperature_2m"],
    "trend": trend_line
}).set_index("time")

# Plot temperature and trend line
st.line_chart(trend_df)

# ============================================
# Precipitation Trend Forecasting
# ============================================

# Precipitation trend using a simple linear regression
st.subheader("Precipitation Trend Forecasting (Linear Regression)")

# Convert time to a numeric index for regression
df["time_index"] = np.arange(len(df))

# Fit a simple linear regression model for precipitation
prec_coeffs = np.polyfit(df["time_index"], df["precipitation"], 1)
prec_trend_line = prec_coeffs[0] * df["time_index"] + prec_coeffs[1]

prec_trend_df = pd.DataFrame({
    "time": df["time"],
    "precipitation": df["precipitation"],
    "trend": prec_trend_line
}).set_index("time")

# Plot precipitation and trend line
st.line_chart(prec_trend_df)

