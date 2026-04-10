import joblib
import pandas as pd
from datetime import datetime, timedelta

model = joblib.load("model.pkl")

def predict_future():
    future_data = []
    current_time = datetime.now()

    for i in range(3):
        future_time = current_time + timedelta(minutes=5 * (i + 1))

        time_numeric = int(future_time.timestamp())
        df = pd.DataFrame([[time_numeric]], columns=["time_numeric"])

        energy = model.predict(df)[0]
        carbon = energy * 0.82

        future_data.append({
            "time": str(future_time),
            "energy_kwh": float(energy),
            "carbon_emission": float(carbon)
        })

    return future_data


def predict_from_input(input_data):
    try:
        print("🔥 RECEIVED DATA:", input_data)

        energy = input_data.get("energy_kwh", 0)

        print("⚡ ENERGY VALUE:", energy)

        energy = float(energy)

        carbon = energy * 0.82

        print("🌱 CARBON:", carbon)

        return {
            "energy_kwh": energy,
            "carbon_emission": carbon
        }

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"error": str(e)}