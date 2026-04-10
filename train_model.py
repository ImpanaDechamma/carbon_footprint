import pandas as pd
import numpy as np
import joblib
import json

from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# -----------------------------------
# 1. LOAD DATA
# -----------------------------------
FILE_PATH = "carbon_footprint_final.csv"
df = pd.read_csv(FILE_PATH)

print("✅ Dataset loaded successfully")
print(df.head())
print("\nColumns:", df.columns.tolist())

# -----------------------------------
# 2. BASIC CHECKS
# -----------------------------------
required_cols = [
    "server_id",
    "timestamp",
    "power_watts",
    "time_diff_hours",
    "energy_kwh",
    "region",
    "emission_factor",
    "carbon_emission"
]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Missing required column: {col}")

# -----------------------------------
# 3. PREPROCESSING
# -----------------------------------
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna().copy()

# Sort properly
df = df.sort_values(["server_id", "timestamp"]).reset_index(drop=True)

# -----------------------------------
# 4. FEATURE ENGINEERING
# -----------------------------------
df["hour"] = df["timestamp"].dt.hour
df["minute"] = df["timestamp"].dt.minute
df["day"] = df["timestamp"].dt.day
df["month"] = df["timestamp"].dt.month
df["day_of_week"] = df["timestamp"].dt.dayofweek

# Cyclic features
df["hour_sin"] = np.sin(2 * np.pi * (df["hour"] * 60 + df["minute"]) / (24 * 60))
df["hour_cos"] = np.cos(2 * np.pi * (df["hour"] * 60 + df["minute"]) / (24 * 60))
df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

# Lag features
for lag in [1, 2, 3]:
    df[f"lag_{lag}"] = df.groupby("server_id")["energy_kwh"].shift(lag)

# Rolling features
for window in [3, 6]:
    df[f"rolling_mean_{window}"] = (
        df.groupby("server_id")["energy_kwh"]
        .transform(lambda x: x.shift(1).rolling(window=window, min_periods=1).mean())
    )
    df[f"rolling_std_{window}"] = (
        df.groupby("server_id")["energy_kwh"]
        .transform(lambda x: x.shift(1).rolling(window=window, min_periods=1).std())
    )

# Fill missing lag/rolling values
numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].median())

# Encode categorical columns
server_encoder = LabelEncoder()
region_encoder = LabelEncoder()

df["server_id_encoded"] = server_encoder.fit_transform(df["server_id"])
df["region_encoded"] = region_encoder.fit_transform(df["region"])

# -----------------------------------
# 5. FEATURES AND TARGET
# -----------------------------------
# Predict energy_kwh first
feature_columns = [
    "power_watts",
    "time_diff_hours",
    "emission_factor",
    "hour",
    "minute",
    "day",
    "month",
    "day_of_week",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "server_id_encoded",
    "region_encoded",
    "lag_1",
    "lag_2",
    "lag_3",
    "rolling_mean_3",
    "rolling_std_3",
    "rolling_mean_6",
    "rolling_std_6"
]

X = df[feature_columns]
y = df["energy_kwh"]

# -----------------------------------
# 6. TRAIN TEST SPLIT
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n✅ Training rows: {len(X_train)}")
print(f"✅ Testing rows: {len(X_test)}")

# -----------------------------------
# 7. MODEL TRAINING
# -----------------------------------
model = ExtraTreesRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# -----------------------------------
# 8. PREDICTION
# -----------------------------------
y_pred = model.predict(X_test)

# carbon emission prediction from predicted energy
carbon_pred = y_pred * X_test["emission_factor"].values
carbon_true = y_test.values * X_test["emission_factor"].values

# -----------------------------------
# 9. METRICS
# -----------------------------------
mae_energy = mean_absolute_error(y_test, y_pred)
rmse_energy = np.sqrt(mean_squared_error(y_test, y_pred))
r2_energy = r2_score(y_test, y_pred)

mae_carbon = mean_absolute_error(carbon_true, carbon_pred)
rmse_carbon = np.sqrt(mean_squared_error(carbon_true, carbon_pred))
r2_carbon = r2_score(carbon_true, carbon_pred)

print("\n📊 ENERGY MODEL METRICS")
print(f"MAE  : {mae_energy:.8f}")
print(f"RMSE : {rmse_energy:.8f}")
print(f"R2   : {r2_energy:.8f}")

print("\n📊 CARBON EMISSION METRICS")
print(f"MAE  : {mae_carbon:.8f}")
print(f"RMSE : {rmse_carbon:.8f}")
print(f"R2   : {r2_carbon:.8f}")

# -----------------------------------
# 10. SAVE MODEL PACKAGE
# -----------------------------------
model_package = {
    "model": model,
    "feature_columns": feature_columns,
    "server_classes": list(server_encoder.classes_),
    "region_classes": list(region_encoder.classes_),
    "default_emission_factor": float(df["emission_factor"].mean())
}

joblib.dump(model_package, "model.pkl")
print("\n✅ Model saved as model.pkl")

# -----------------------------------
# 11. SAVE METRICS
# -----------------------------------
metrics = {
    "MAE_energy_kwh": float(round(mae_energy, 8)),
    "RMSE_energy_kwh": float(round(rmse_energy, 8)),
    "R2_energy_kwh": float(round(r2_energy, 8)),
    "MAE_carbon_emission": float(round(mae_carbon, 8)),
    "RMSE_carbon_emission": float(round(rmse_carbon, 8)),
    "R2_carbon_emission": float(round(r2_carbon, 8)),
    "model_used": "ExtraTreesRegressor"
}

with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("✅ Metrics saved as metrics.json")

# -----------------------------------
# 12. SAVE FEATURE IMPORTANCE
# -----------------------------------
feature_importance = pd.DataFrame({
    "Feature": feature_columns,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

feature_importance.to_csv("feature_importance.csv", index=False)
print("✅ Feature importance saved as feature_importance.csv")

print("\nTop Feature Importance:")
print(feature_importance.head(10))