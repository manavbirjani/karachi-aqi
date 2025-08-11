import os
import pandas as pd
import joblib
from datetime import datetime, timedelta

MODEL_PATH = "models/karachi_aqi_model.pkl"

def forecast_next_3_days():
    model = joblib.load(MODEL_PATH)

    now = datetime.utcnow()
    forecast_rows = []
    for i in range(1, 4):
        date = now + timedelta(days=i)
        features = pd.DataFrame([{
            "pm25": 100.0,  # placeholder
            "pm10": 50.0,   # placeholder
            "o3": 30.0,     # placeholder
            "co": 0.4,      # placeholder
            "no2": 15.0,    # placeholder
            "so2": 5.0,     # placeholder
            "hour": 12,
            "day": date.day,
            "month": date.month
        }])
        predicted_aqi = model.predict(features)[0]
        forecast_rows.append({
            "date": date.date(),
            "predicted_aqi": predicted_aqi
        })

    forecast_df = pd.DataFrame(forecast_rows)
    os.makedirs("data", exist_ok=True)
    forecast_df.to_csv("data/forecast_3day.csv", index=False)
    print("3-day forecast saved to data/forecast_3day.csv")

if __name__ == "__main__":
    forecast_next_3_days()
