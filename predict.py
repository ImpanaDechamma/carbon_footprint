import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


MODEL_FILE = "model_bundle.pkl"

bundle = joblib.load(MODEL_FILE)
model = bundle["model"]
feature_cols = bundle["feature_cols"]
default_emission_factor = bundle["default_emission_factor"]
default_time_diff_hours = bundle["default_time_diff_hours"]
latest_history = bundle["latest_history"]


def make_time_features(timestamp: pd.Timestamp) -> dict:
    hour = timestamp.hour
    day = timestamp.day
    day_of_week = timestamp.dayofweek
    month = timestamp.month
    is_weekend = 1 if day_of_week in [5, 6] else 0

    return {
        "hour": hour,
        "day": day,
        "day_of_week": day_of_week,
        "month": month,
        "is_weekend": is_weekend,
        "hour_sin": np.sin(2 * np.pi * hour / 24),
        "hour_cos": np.cos(2 * np.pi * hour / 24),
        "dow_sin": np.sin(2 * np.pi * day_of_week / 7),
        "dow_cos": np.cos(2 * np.pi * day_of_week / 7),
    }


def get_server_history(server_id: str) -> pd.DataFrame:
    server_df = latest_history[latest_history["server_id"] == server_id].sort_values("timestamp")
    if len(server_df) < 3:
        raise ValueError(f"Not enough history available for server_id={server_id}")
    return server_df


def build_feature_row(
    server_id: str,
    region: str,
    timestamp: pd.Timestamp,
    time_diff_hours: float,
    lag_1: float,
    lag_2: float,
    lag_3: float,
) -> pd.DataFrame:
    row = {
        "server_id": server_id,
        "region": region,
        "time_diff_hours": time_diff_hours,
        "lag_1": lag_1,
        "lag_2": lag_2,
        "lag_3": lag_3,
        "rolling_mean_3": float(np.mean([lag_1, lag_2, lag_3])),
        "rolling_std_3": float(np.std([lag_1, lag_2, lag_3])),
    }

    row.update(make_time_features(timestamp))

    return pd.DataFrame([row])[feature_cols]


def predict_from_input(input_data: dict) -> dict:
    try:
        server_id = str(input_data["server_id"])
        region = str(input_data["region"])
        timestamp_str = input_data.get("timestamp")
        timestamp = pd.to_datetime(timestamp_str) if timestamp_str else pd.Timestamp(datetime.now())

        time_diff_hours = float(input_data.get("time_diff_hours", default_time_diff_hours))
        emission_factor = float(input_data.get("emission_factor", default_emission_factor))

        history = get_server_history(server_id)
        power_values = history["power_watts"].tolist()

        lag_1 = float(power_values[-1])
        lag_2 = float(power_values[-2])
        lag_3 = float(power_values[-3])

        X = build_feature_row(
            server_id=server_id,
            region=region,
            timestamp=timestamp,
            time_diff_hours=time_diff_hours,
            lag_1=lag_1,
            lag_2=lag_2,
            lag_3=lag_3,
        )

        predicted_power = float(model.predict(X)[0])
        predicted_energy = float((predicted_power * time_diff_hours) / 1000)
        predicted_carbon = float(predicted_energy * emission_factor)

        return {
            "server_id": server_id,
            "region": region,
            "timestamp": str(timestamp),
            "predicted_power_watts": round(predicted_power, 4),
            "predicted_energy_kwh": round(predicted_energy, 6),
            "predicted_carbon_emission": round(predicted_carbon, 6),
            "time_diff_hours_used": round(time_diff_hours, 6),
            "emission_factor_used": round(emission_factor, 6),
        }

    except Exception as e:
        return {"error": str(e)}


def predict_future(server_id: str, region: str, steps: int = 3, interval_minutes: int = 5,
                   emission_factor: float = None, time_diff_hours: float = None) -> list:
    try:
        if emission_factor is None:
            emission_factor = default_emission_factor
        if time_diff_hours is None:
            time_diff_hours = default_time_diff_hours

        history = get_server_history(server_id)
        history = history.sort_values("timestamp")

        current_time = pd.to_datetime(history["timestamp"].iloc[-1])
        lag_1 = float(history["power_watts"].iloc[-1])
        lag_2 = float(history["power_watts"].iloc[-2])
        lag_3 = float(history["power_watts"].iloc[-3])

        future_results = []

        for i in range(steps):
            future_time = current_time + timedelta(minutes=interval_minutes * (i + 1))

            X = build_feature_row(
                server_id=server_id,
                region=region,
                timestamp=future_time,
                time_diff_hours=time_diff_hours,
                lag_1=lag_1,
                lag_2=lag_2,
                lag_3=lag_3,
            )

            predicted_power = float(model.predict(X)[0])
            predicted_energy = float((predicted_power * time_diff_hours) / 1000)
            predicted_carbon = float(predicted_energy * emission_factor)

            future_results.append({
                "time": str(future_time),
                "predicted_power_watts": round(predicted_power, 4),
                "predicted_energy_kwh": round(predicted_energy, 6),
                "predicted_carbon_emission": round(predicted_carbon, 6),
            })

            # recursive lag update
            lag_3 = lag_2
            lag_2 = lag_1
            lag_1 = predicted_power

        return future_results

    except Exception as e:
        return [{"error": str(e)}]