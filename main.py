from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

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
def encode_value(value, classes_list):
    value = str(value)
    if value in classes_list:
        return classes_list.index(value)
    return 0


def build_feature_row(input_data):
    server_id = str(input_data.get("server_id", "S1"))
    region = str(input_data.get("region", "India"))

    power_watts = float(input_data.get("power_watts", 100))
    time_diff_hours = float(input_data.get("time_diff_hours", 0.083333))
    energy_kwh = float(input_data.get("energy_kwh", (power_watts * time_diff_hours) / 1000))
    emission_factor = float(input_data.get("emission_factor", 0.82))

    timestamp_str = input_data.get("timestamp")
    if timestamp_str:
        timestamp = pd.to_datetime(timestamp_str, errors="coerce")
        if pd.isna(timestamp):
            timestamp = datetime.now()
    else:
        timestamp = datetime.now()

    hour = timestamp.hour
    minute = timestamp.minute
    day = timestamp.day
    month = timestamp.month
    day_of_week = timestamp.weekday()

    hour_sin = np.sin(2 * np.pi * (hour * 60 + minute) / (24 * 60))
    hour_cos = np.cos(2 * np.pi * (hour * 60 + minute) / (24 * 60))
    dow_sin = np.sin(2 * np.pi * day_of_week / 7)
    dow_cos = np.cos(2 * np.pi * day_of_week / 7)

    # If lag features are not supplied, use current values as fallback
    power_lag_1 = float(input_data.get("power_lag_1", power_watts))
    power_lag_2 = float(input_data.get("power_lag_2", power_watts))
    power_lag_3 = float(input_data.get("power_lag_3", power_watts))

    energy_lag_1 = float(input_data.get("energy_lag_1", energy_kwh))
    energy_lag_2 = float(input_data.get("energy_lag_2", energy_kwh))
    energy_lag_3 = float(input_data.get("energy_lag_3", energy_kwh))

    power_roll_mean_3 = float(input_data.get("power_roll_mean_3", power_watts))
    power_roll_std_3 = float(input_data.get("power_roll_std_3", 0))
    power_roll_mean_6 = float(input_data.get("power_roll_mean_6", power_watts))
    power_roll_std_6 = float(input_data.get("power_roll_std_6", 0))

    energy_roll_mean_3 = float(input_data.get("energy_roll_mean_3", energy_kwh))
    energy_roll_std_3 = float(input_data.get("energy_roll_std_3", 0))
    energy_roll_mean_6 = float(input_data.get("energy_roll_mean_6", energy_kwh))
    energy_roll_std_6 = float(input_data.get("energy_roll_std_6", 0))

    server_id_encoded = encode_value(server_id, server_classes)
    region_encoded = encode_value(region, region_classes)

    row = {
        "power_watts": power_watts,
        "time_diff_hours": time_diff_hours,
        "energy_kwh": energy_kwh,
        "emission_factor": emission_factor,
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
        "power_lag_1": power_lag_1,
        "power_lag_2": power_lag_2,
        "power_lag_3": power_lag_3,
        "energy_lag_1": energy_lag_1,
        "energy_lag_2": energy_lag_2,
        "energy_lag_3": energy_lag_3,
        "power_roll_mean_3": power_roll_mean_3,
        "power_roll_std_3": power_roll_std_3,
        "power_roll_mean_6": power_roll_mean_6,
        "power_roll_std_6": power_roll_std_6,
        "energy_roll_mean_3": energy_roll_mean_3,
        "energy_roll_std_3": energy_roll_std_3,
        "energy_roll_mean_6": energy_roll_mean_6,
        "energy_roll_std_6": energy_roll_std_6
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
        input_data = request.get_json()

        if not input_data:
            return jsonify({
                "success": False,
                "error": "No input data received"
            }), 400

        features_df = build_feature_row(input_data)
        carbon_prediction = model.predict(features_df)[0]

        return jsonify({
            "success": True,
            "predicted_carbon_emission": round(float(carbon_prediction), 8),
            "unit": "kg CO2"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)