import pandas as pd
import numpy as np
import joblib
import json

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# -----------------------------------
# 1. LOAD DATA
# -----------------------------------
FILE_PATH = "carbon_footprint_final.csv"
df = pd.read_csv(FILE_PATH)

print("✅ Dataset loaded successfully")
print(df.head())
print("\nColumns in dataset:", df.columns.tolist())

# -----------------------------------
# 2. CHECK REQUIRED COLUMNS
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
df = df.sort_values(["server_id", "timestamp"]).reset_index(drop=True)

print(f"\n✅ Rows after cleaning: {len(df)}")

# -----------------------------------
# 4. FEATURE ENGINEERING
# -----------------------------------
df["hour"] = df["timestamp"].dt.hour
df["minute"] = df["timestamp"].dt.minute
df["day"] = df["timestamp"].dt.day
df["month"] = df["timestamp"].dt.month
df["day_of_week"] = df["timestamp"].dt.dayofweek

df["hour_sin"] = np.sin(2 * np.pi * (df["hour"] * 60 + df["minute"]) / (24 * 60))
df["hour_cos"] = np.cos(2 * np.pi * (df["hour"] * 60 + df["minute"]) / (24 * 60))
df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

for lag in [1, 2, 3]:
    df[f"lag_{lag}"] = df.groupby("server_id")["energy_kwh"].shift(lag)

for window in [3, 6]:
    df[f"rolling_mean_{window}"] = (
        df.groupby("server_id")["energy_kwh"]
        .transform(lambda x: x.shift(1).rolling(window=window, min_periods=1).mean())
    )
    df[f"rolling_std_{window}"] = (
        df.groupby("server_id")["energy_kwh"]
        .transform(lambda x: x.shift(1).rolling(window=window, min_periods=1).std())
    )

numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].median())

# -----------------------------------
# 5. ENCODE CATEGORICAL COLUMNS
# -----------------------------------
server_encoder = LabelEncoder()
region_encoder = LabelEncoder()

df["server_id_encoded"] = server_encoder.fit_transform(df["server_id"])
df["region_encoded"] = region_encoder.fit_transform(df["region"])

# -----------------------------------
# 6. SELECT FEATURES AND TARGET
# -----------------------------------
# NOTE: energy_kwh and emission_factor are excluded intentionally —
# keeping them makes carbon_emission trivially predictable (R2=1)
# since carbon = energy_kwh * emission_factor by definition.
feature_columns = [
    "power_watts",
    "time_diff_hours",
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
y = df["carbon_emission"]

print("\n✅ Features selected:")
print(feature_columns)
print("\n✅ Target selected: carbon_emission")

# -----------------------------------
# 7. SPLIT DATA INTO TRAIN AND TEST
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n✅ Training rows: {len(X_train)}")
print(f"✅ Testing rows: {len(X_test)}")

# -----------------------------------
# 8. TRAIN MODEL
# -----------------------------------
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("\n✅ Random Forest model training completed")

# -----------------------------------
# 9. MAKE PREDICTIONS
# -----------------------------------
y_pred = model.predict(X_test)

# -----------------------------------
# 10. EVALUATE MODEL
# -----------------------------------
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("\n📊 CARBON EMISSION MODEL METRICS")
print(f"MAE  : {mae:.8f}")
print(f"MSE  : {mse:.8f}")
print(f"RMSE : {rmse:.8f}")
print(f"R2   : {r2:.8f}")

# -----------------------------------
# 11. SAVE MODEL
# -----------------------------------
model_package = {
    "model": model,
    "feature_columns": feature_columns,
    "server_classes": list(server_encoder.classes_),
    "region_classes": list(region_encoder.classes_)
}

joblib.dump(model_package, "model.pkl")
print("\n✅ Model saved as model.pkl")

# -----------------------------------
# 12. SAVE METRICS
# -----------------------------------
metrics = {
    "MAE_carbon_emission": float(round(mae, 8)),
    "MSE_carbon_emission": float(round(mse, 8)),
    "RMSE_carbon_emission": float(round(rmse, 8)),
    "R2_carbon_emission": float(round(r2, 8)),
    "model_used": "RandomForestRegressor"
}

with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("✅ Metrics saved as metrics.json")

# -----------------------------------
# 13. SAVE FEATURE IMPORTANCE
# -----------------------------------
feature_importance = pd.DataFrame({
    "Feature": feature_columns,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

feature_importance.to_csv("feature_importance.csv", index=False)

print("✅ Feature importance saved as feature_importance.csv")
print("\nTop 10 Important Features:")
print(feature_importance.head(10))