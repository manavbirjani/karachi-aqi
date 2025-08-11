import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
import os

def forecast_next_3_days():
    # Load trained model
    with open("models/karachi_aqi_model.pkl", "rb") as f:
        model = pickle.load(f)

    # Load latest pollutant features
    latest_features_file = "data/features_karachi.csv"
    if not os.path.exists(latest_features_file):
        raise FileNotFoundError("features_karachi.csv not found!")

    features_df = pd.read_csv(latest_features_file)
    if features_df.empty:
        raise ValueError("features_karachi.csv is empty!")

    # Get averages
    avg_pm25 = features_df["pm25"].mean()
    avg_pm10 = features_df["pm10"].mean()
    avg_o3 = features_df["o3"].mean()
    avg_co = features_df.get("co", pd.Series([0])).mean()
    avg_no2 = features_df.get("no2", pd.Series([0])).mean()
    avg_so2 = features_df.get("so2", pd.Series([0])).mean()
    avg_pm25_change = features_df.get("pm25_change", pd.Series([0])).mean()

    # Forecast data for next 3 days (every 3 hours)
    forecast_data = []
    now = datetime.now()

    for i in range(24):  # 24 * 3-hour intervals
        future_time = now + timedelta(hours=i * 3)
        row = {
            "pm25": avg_pm25,
            "pm10": avg_pm10,
            "o3": avg_o3,
            "co": avg_co,
            "no2": avg_no2,
            "so2": avg_so2,
            "pm25_change": avg_pm25_change,
            "hour": future_time.hour,
            "day": future_time.day,
            "month": future_time.month
        }
        forecast_data.append(row)

    forecast_df = pd.DataFrame(forecast_data)

    # Ensure all required features exist and in correct order
    for col in model.feature_names_in_:
        if col not in forecast_df.columns:
            forecast_df[col] = 0  # add missing columns
    forecast_df = forecast_df[model.feature_names_in_]  # reorder to match training

    # Predict AQI
    forecast_df["predicted_aqi"] = model.predict(forecast_df)
    forecast_df["prediction_time"] = [now + timedelta(hours=i * 3) for i in range(24)]

    # Save to CSV
    output_path = "data/forecast_3day.csv"
    forecast_df.to_csv(output_path, index=False)
    print(f"Forecast saved to {output_path}")

if __name__ == "__main__":
    forecast_next_3_days()
