import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
import joblib

df = pd.read_csv("carbon_footprint_final.csv")

df['timestamp'] = pd.to_datetime(df['timestamp'])

processed_df = df.copy()

if 'carbon_emission' not in processed_df.columns:
    processed_df['carbon_emission'] = (
        processed_df['energy_kwh'] * processed_df['emission_factor']
    )

print("✅ Processing Complete!")
print(processed_df.head())

client = MongoClient("mongodb://localhost:27017/")
db = client["carbon_db"]
collection = db["emissions"]

data_dict = processed_df.to_dict(orient="records")

collection.insert_many(data_dict)

print("✅ Data inserted into MongoDB successfully!")

processed_df['time_numeric'] = processed_df['timestamp'].astype('int64') // 10**9

X = processed_df[['time_numeric']]
y = processed_df['energy_kwh']


model = LinearRegression()
model.fit(X, y)

print("✅ Model trained successfully!")

joblib.dump(model, "model.pkl")

print("✅ Model saved as model.pkl")