import os
import requests
import pandas as pd
import joblib
from datetime import datetime

API_TOKEN = os.getenv("AQI_API_TOKEN")
CITY = "karachi"
MODEL_PATH = "models/karachi_aqi_model.pkl"

def fetch_live_data():
    url = f"https://api.waqi.info/feed/{CITY}/?token={API_TOKEN}"
    response = requests.get(url)
    data = response.json()

    pm25 = data["data"]["iaqi"].get("pm25", {}).get("v", 0.0)
    pm10 = data["data"]["iaqi"].get("pm10", {}).get("v", 0.0)
    o3 = data["data"]["iaqi"].get("o3", {}).get("v", 0.0)
    co = data["data"]["iaqi"].get("co", {}).get("v", 0.0)
    no2 = data["data"]["iaqi"].get("no2", {}).get("v", 0.0)
    so2 = data["data"]["iaqi"].get("so2", {}).get("v", 0.0)

    now = datetime.utcnow()
    features = pd.DataFrame([{
        "pm25": pm25,
        "pm10": pm10,
        "o3": o3,
        "co": co,
        "no2": no2,
        "so2": so2,
        "hour": now.hour,
        "day": now.day,
        "month": now.month
    }])
    return features

if __name__ == "__main__":
    model = joblib.load(MODEL_PATH)

    X_today = fetch_live_data()
    print("Features used for prediction:")
    print(X_today)

    prediction = model.predict(X_today)[0]
    print(f"Predicted AQI: {prediction:.2f}")

    os.makedirs("data", exist_ok=True)
    pred_file = "data/daily_predictions.csv"

    df = pd.DataFrame([{
        "timestamp": datetime.utcnow().isoformat(),
        "predicted_aqi": prediction
    }])

    if os.path.exists(pred_file):
        df.to_csv(pred_file, mode="a", header=False, index=False)
    else:
        df.to_csv(pred_file, index=False)

    print(f"Prediction saved to {pred_file}")
