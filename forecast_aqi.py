# forecast_aqi.py (replace)
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta

MODEL_PATH = "models/karachi_aqi_model.pkl"
LATEST_FEATURES = "data/features_karachi.csv"  # or data/features_store.csv
OUTPUT = "data/forecast_3day.csv"

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Run training first.")
    return joblib.load(MODEL_PATH)

def get_base_averages():
    if not os.path.exists(LATEST_FEATURES):
        raise FileNotFoundError(f"{LATEST_FEATURES} not found.")
    df = pd.read_csv(LATEST_FEATURES)
    return {
        "pm25": df.get("pm25", pd.Series([0])).mean(),
        "pm10": df.get("pm10", pd.Series([0])).mean(),
        "o3": df.get("o3", pd.Series([0])).mean(),
        "co": df.get("co", pd.Series([0])).mean(),
        "no2": df.get("no2", pd.Series([0])).mean(),
        "so2": df.get("so2", pd.Series([0])).mean(),
    }

def forecast_next_3_days():
    model = load_model()
    base = get_base_averages()
    now = datetime.now()
    rows = []
    for i in range(24):  # every 3 hours, 24 points = 3 days
        t = now + timedelta(hours=3*i)
        rows.append({
            "pm25": base["pm25"],
            "pm10": base["pm10"],
            "o3": base["o3"],
            "co": base["co"],
            "no2": base["no2"],
            "so2": base["so2"],
            "hour": t.hour,
            "day": t.day,
            "month": t.month,
            "pm25_change": 0.0,
            "prediction_time": t.strftime("%Y-%m-%d %H:%M:%S")
        })
    df = pd.DataFrame(rows)
    # align to model features
    if hasattr(model, "feature_names_in_"):
        feature_names = list(model.feature_names_in_)
    else:
        feature_names = ["pm25","pm10","o3","co","no2","so2","hour","day","month","pm25_change"]
    # ensure columns present
    for c in feature_names:
        if c not in df.columns:
            df[c] = 0.0
    X = df[feature_names]
    df["predicted_aqi"] = model.predict(X)
    df.to_csv(OUTPUT, index=False)
    print("Forecast saved to", OUTPUT)

if __name__ == "__main__":
    forecast_next_3_days()
