"""
Run once to load carbon_footprint_final.csv into MongoDB.
    python seed_db.py
"""
import pandas as pd
from db import ensure_timeseries, insert_many_readings

df = pd.read_csv("carbon_footprint_final.csv")
df.columns = df.columns.str.strip()
df["timestamp"] = pd.to_datetime(df["timestamp"])

ensure_timeseries()

records = df.to_dict(orient="records")
insert_many_readings(records)
print("✅ Seeding complete.")
