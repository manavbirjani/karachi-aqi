import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import mlflow
import mlflow.sklearn

# Load the CSV data
df = pd.read_csv("data/raw_aqi_data_karachi.csv")

# Fix columns
df.rename(columns={"03": "o3"}, inplace=True)
df.rename(columns={"datetime": "timestamp"}, inplace=True)

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df.dropna(subset=["timestamp"], inplace=True)

# Fill missing pollutants with 0 if any column is missing
for col in ["pm25", "pm10", "o3", "co", "no2", "so2"]:
    if col not in df.columns:
        df[col] = 0.0

# Extract time-based features
df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.day
df["month"] = df["timestamp"].dt.month

# Features and Target
features = ["pm25", "pm10", "o3", "co", "no2", "so2", "hour", "day", "month"]
X = df[features]
y = df["aqi"]

# Train Model
model = RandomForestRegressor(max_depth=10)
model.fit(X, y)

# Evaluate
y_pred = model.predict(X)
rmse = np.sqrt(mean_squared_error(y, y_pred))
print(f"✅ Model Trained | RMSE: {rmse:.2f}")

# Save model locally
with open("models/karachi_aqi_model.pkl", "wb") as f:
    pickle.dump(model, f)

# Track with MLflow
mlflow.set_experiment("Karachi_AQI_Model")

with mlflow.start_run():
    mlflow.log_params({
        "model": "RandomForest",
        "max_depth": 10
    })
    mlflow.log_metric("rmse", rmse)
    mlflow.sklearn.log_model(model, "random_forest_model")

print("✅ Model & metrics logged in MLflow")
