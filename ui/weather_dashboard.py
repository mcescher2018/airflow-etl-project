import duckdb
import pandas as pd
import streamlit as st

# ============================================
# Configuration
# ============================================
DB_PATH = "../airflow/data/weather.duckdb"
TABLE_NAME = "weather_data"

# Expected DAG frequency in hours (change as needed)
EXPECTED_PERIOD_HOURS = 2  

# ============================================
# Connect to DuckDB
# ============================================
con = duckdb.connect(DB_PATH)

st.title("Weather Data – KPI Dashboard")

# ============================================
# Weather Historical Data
# ============================================
st.header("Weather Historical Data")

df_trend = con.execute(f"""
    SELECT time, temperature_2m, precipitation
    FROM {TABLE_NAME}
    ORDER BY time
""").fetchdf()

st.line_chart(df_trend.set_index("time"))

# ============================================
# KPI 1 — Duplicate primary keys
# ============================================
st.header("KPI: Duplicate Primary Keys (time)")
df_dups = con.execute(f"""
    SELECT time, COUNT(*) AS cnt
    FROM {TABLE_NAME}
    GROUP BY time
    HAVING COUNT(*) > 1
""").fetchdf()

st.metric("Duplicate timestamps", len(df_dups))
if len(df_dups) > 0:
    st.dataframe(df_dups)

# ============================================
# KPI 2 — Temporal gaps larger than expected
# ============================================
st.header("KPI: Temporal Gaps > Expected Frequency")

df_gaps = con.execute(f"""
    WITH ordered AS (
        SELECT 
            time,
            LEAD(time) OVER (ORDER BY time) AS next_time
        FROM {TABLE_NAME}
    )
    SELECT 
        time,
        next_time,
        EXTRACT(EPOCH FROM (next_time - time)) / 3600 AS gap_hours
    FROM ordered
    WHERE next_time IS NOT NULL
      AND EXTRACT(EPOCH FROM (next_time - time)) / 3600 > {EXPECTED_PERIOD_HOURS} * 1.3
""").fetchdf()

st.metric("Gaps > expected", len(df_gaps))
if len(df_gaps) > 0:
    st.dataframe(df_gaps)

# ============================================
# KPI 3 — Impossible values
# ============================================
st.header("KPI: Impossible Values")

df_bad_values = con.execute(f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE temperature_2m < -80
       OR temperature_2m > 80
       OR precipitation < 0
       OR precipitation > 500
""").fetchdf()

st.metric("Impossible values", len(df_bad_values))
if len(df_bad_values) > 0:
    st.dataframe(df_bad_values)

# ============================================
# KPI 4 — NULL values
# ============================================
st.header("KPI: NULL Values")

df_nulls = con.execute(f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE temperature_2m IS NULL
       OR precipitation IS NULL
""").fetchdf()

st.metric("NULL records", len(df_nulls))
if len(df_nulls) > 0:
    st.dataframe(df_nulls)

# ============================================
# KPI 5 — Updated records (modified_date > creation_date)
# ============================================
st.header("KPI: Updated Records")

df_updates = con.execute(f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE modified_date > creation_date
""").fetchdf()

st.metric("Updated records", len(df_updates))
if len(df_updates) > 0:
    st.dataframe(df_updates)

# ============================================
# KPI 6 — Daily record distribution
# ============================================
st.header("Daily Record Distribution")

df_daily = con.execute(f"""
    SELECT DATE(time) AS day, COUNT(*) AS records
    FROM {TABLE_NAME}
    GROUP BY day
    ORDER BY day
""").fetchdf()

st.dataframe(df_daily)