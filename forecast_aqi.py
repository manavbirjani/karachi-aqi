# src/forecast_aqi.py
"""
3-day AQI forecast script.
Generates predictions for every 3 hours for the next 3 days using the trained model.
"""

import pandas as pd
import joblib
import os
from datetime import datetime, timedelta

MODEL_PATH = "models/karachi_aqi_model.pkl"
FEATURES_PATH = "data/features_store.csv"
OUTPUT_PATH = "data/forecast_3day.csv"

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

def load_latest_features():
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"Features file not found: {FEATURES_PATH}")
    
    df = pd.read_csv(FEATURES_PATH)
    if df.empty:
        raise ValueError(f"No data found in {FEATURES_PATH}")

    avg_values = {}
    for col in df.columns:
        if col != "timestamp":  # timestamp ko skip karte hain
            avg_values[col] = df[col].mean()
    
    return avg_values

def forecast_next_3_days():
    model = load_model()
    avg_values = load_latest_features()

    now = datetime.now()
    forecast_data = []

    for i in range(24):  # 3 days * 8 intervals
        future_time = now + timedelta(hours=i*3)
        row = avg_values.copy()

        # Agar hour/day/month training me the to add karein
        row["hour"] = future_time.hour
        row["day"] = future_time.day
        row["month"] = future_time.month

        forecast_data.append(row)

    forecast_df = pd.DataFrame(forecast_data)

    # Ensure order matches training
    if hasattr(model, "feature_names_in_"):
        forecast_df = forecast_df[model.feature_names_in_]

    forecast_df["predicted_aqi"] = model.predict(forecast_df)
    forecast_df["prediction_time"] = [now + timedelta(hours=i*3) for i in range(24)]

    forecast_df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Forecast saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    forecast_next_3_days()
