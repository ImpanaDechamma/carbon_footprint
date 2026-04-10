from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import json

app = Flask(__name__)
CORS(app)

# -----------------------------------
# LOAD MODEL PACKAGE
# -----------------------------------
model_package = joblib.load("model.pkl")

model = model_package["model"]
feature_columns = model_package["feature_columns"]
server_classes = model_package["server_classes"]
region_classes = model_package["region_classes"]

# -----------------------------------
# HELPER FUNCTIONS
# -----------------------------------
def safe_encode(value, classes):
    if value in classes:
        return classes.index(value)
    return 0

def prepare_input(data):
    server_id = data.get("server_id", server_classes[0] if server_classes else "S1")
    region = data.get("region", region_classes[0] if region_classes else "USA")
    energy_kwh = float(data.get("energy_kwh", 0))

    timestamp_str = data.get("timestamp", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
    timestamp = pd.to_datetime(timestamp_str, errors="coerce")
    if pd.isna(timestamp):
        timestamp = pd.Timestamp.now()

    hour = timestamp.hour
    minute = timestamp.minute
    day = timestamp.day
    month = timestamp.month
    day_of_week = timestamp.dayofweek

    hour_sin = np.sin(2 * np.pi * (hour * 60 + minute) / (24 * 60))
    hour_cos = np.cos(2 * np.pi * (hour * 60 + minute) / (24 * 60))
    dow_sin = np.sin(2 * np.pi * day_of_week / 7)
    dow_cos = np.cos(2 * np.pi * day_of_week / 7)

    lag_1 = float(data.get("lag_1", energy_kwh))
    lag_2 = float(data.get("lag_2", energy_kwh))
    lag_3 = float(data.get("lag_3", energy_kwh))
    rolling_mean_3 = float(data.get("rolling_mean_3", energy_kwh))
    rolling_std_3 = float(data.get("rolling_std_3", 0))
    rolling_mean_6 = float(data.get("rolling_mean_6", energy_kwh))
    rolling_std_6 = float(data.get("rolling_std_6", 0))

    server_id_encoded = safe_encode(server_id, server_classes)
    region_encoded = safe_encode(region, region_classes)

    row = {
        "power_watts": float(data.get("power_watts", 0)),
        "time_diff_hours": float(data.get("time_diff_hours", 0.083333)),
        "hour": hour,
        "minute": minute,
        "day": day,
        "month": month,
        "day_of_week": day_of_week,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "dow_sin": dow_sin,
        "dow_cos": dow_cos,
        "server_id_encoded": server_id_encoded,
        "region_encoded": region_encoded,
        "lag_1": lag_1,
        "lag_2": lag_2,
        "lag_3": lag_3,
        "rolling_mean_3": rolling_mean_3,
        "rolling_std_3": rolling_std_3,
        "rolling_mean_6": rolling_mean_6,
        "rolling_std_6": rolling_std_6
    }

    return pd.DataFrame([row])[feature_columns]

# -----------------------------------
# ROUTES
# -----------------------------------
@app.route("/")
def home():
    return "Carbon Emission Prediction API is running!"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        input_df = prepare_input(data)
        predicted_carbon = float(model.predict(input_df)[0])

        # persist prediction to MongoDB
        try:
            from db import insert_reading
            from datetime import datetime
            ts_str = data.get("timestamp")
            ts = pd.to_datetime(ts_str) if ts_str else datetime.utcnow()
            insert_reading(
                server_id       = data.get("server_id", "unknown"),
                region          = data.get("region", "unknown"),
                power_watts     = float(data.get("power_watts", 0)),
                time_diff_hours = float(data.get("time_diff_hours", 0.083333)),
                energy_kwh      = float(data.get("energy_kwh", 0)),
                emission_factor = float(data.get("emission_factor", 0)),
                carbon_emission = predicted_carbon,
                timestamp       = ts
            )
        except Exception:
            pass  # DB failure must not break the API response

        return jsonify({
            "success": True,
            "predicted_carbon_emission": round(predicted_carbon, 6)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        with open("metrics.json", "r") as f:
            metrics = json.load(f)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)