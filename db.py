from pymongo import MongoClient, ASCENDING
from datetime import datetime
import pandas as pd

# ── Connection ──────────────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017/"   # replace with Atlas URI if using cloud
DB_NAME   = "carbon_footprint"
COL_NAME  = "server_metrics"

_client = None

def get_collection():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client[DB_NAME][COL_NAME]


def ensure_timeseries():
    """Create a time-series collection once (skips if already exists)."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    if COL_NAME not in db.list_collection_names():
        db.create_collection(
            COL_NAME,
            timeseries={
                "timeField": "timestamp",
                "metaField":  "metadata",
                "granularity": "minutes"
            }
        )
        print(f"✅ Time-series collection '{COL_NAME}' created.")
    else:
        print(f"ℹ️  Collection '{COL_NAME}' already exists.")


# ── Write ────────────────────────────────────────────────────────────────────
def insert_reading(server_id, region, power_watts,
                   time_diff_hours, energy_kwh,
                   emission_factor, carbon_emission,
                   timestamp=None):
    """Insert a single server reading."""
    col = get_collection()
    doc = {
        "timestamp": timestamp or datetime.utcnow(),
        "metadata": {
            "server_id": server_id,
            "region":    region
        },
        "power_watts":      power_watts,
        "time_diff_hours":  time_diff_hours,
        "energy_kwh":       energy_kwh,
        "emission_factor":  emission_factor,
        "carbon_emission":  carbon_emission
    }
    col.insert_one(doc)


def insert_many_readings(records: list[dict]):
    """Bulk insert a list of reading dicts (same shape as insert_reading)."""
    col = get_collection()
    docs = [
        {
            "timestamp": r.get("timestamp", datetime.utcnow()),
            "metadata": {
                "server_id": r["server_id"],
                "region":    r["region"]
            },
            "power_watts":     r["power_watts"],
            "time_diff_hours": r["time_diff_hours"],
            "energy_kwh":      r["energy_kwh"],
            "emission_factor": r["emission_factor"],
            "carbon_emission": r["carbon_emission"]
        }
        for r in records
    ]
    col.insert_many(docs)
    print(f"✅ Inserted {len(docs)} records.")


# ── Read ─────────────────────────────────────────────────────────────────────
def query_readings(server_id=None, start=None, end=None) -> pd.DataFrame:
    """
    Fetch readings as a DataFrame.
    All parameters are optional — omit to get everything.
    """
    col   = get_collection()
    match = {}

    if server_id:
        match["metadata.server_id"] = server_id
    if start or end:
        match["timestamp"] = {}
        if start:
            match["timestamp"]["$gte"] = pd.to_datetime(start)
        if end:
            match["timestamp"]["$lte"] = pd.to_datetime(end)

    cursor = col.find(match, {"_id": 0}).sort("timestamp", ASCENDING)
    docs   = list(cursor)

    if not docs:
        return pd.DataFrame()

    df = pd.DataFrame(docs)
    df["server_id"] = df["metadata"].apply(lambda x: x["server_id"])
    df["region"]    = df["metadata"].apply(lambda x: x["region"])
    df.drop(columns=["metadata"], inplace=True)
    return df


def get_latest_n(server_id, n=3) -> pd.DataFrame:
    """Return the last n readings for a given server (used for lag features)."""
    col  = get_collection()
    docs = list(
        col.find({"metadata.server_id": server_id}, {"_id": 0})
           .sort("timestamp", -1)
           .limit(n)
    )
    if not docs:
        return pd.DataFrame()
    df = pd.DataFrame(docs)
    df["server_id"] = df["metadata"].apply(lambda x: x["server_id"])
    df["region"]    = df["metadata"].apply(lambda x: x["region"])
    df.drop(columns=["metadata"], inplace=True)
    return df.sort_values("timestamp")
