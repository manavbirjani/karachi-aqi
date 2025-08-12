import os
import pandas as pd
import joblib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("AQI_API_TOKEN")
CITY = "karachi"
MODEL_PATH = "models/karachi_aqi_model.pkl"
PREDICTIONS_FILE = "data/daily_predictions.csv"

def fetch_live_data():
    if not API_TOKEN:
        raise ValueError("API token not found. Please set AQI_API_TOKEN in .env file.")
    url = f"https://api.waqi.info/feed/{CITY}/?token={API_TOKEN}"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"API request failed with status {response.status_code}")
    data = response.json()
    if data.get("status") != "ok":
        raise ValueError(f"API returned error: {data}")
    iaqi = data["data"]["iaqi"]
    now = datetime.now()

    features = {
        "pm25_change": 1.0,  # fixed test value for pm25_change
        "pm10": iaqi.get("pm10", {}).get("v", 0.0),
        "o3": iaqi.get("o3", {}).get("v", 0.0),
        "hour": now.hour,
        "day": now.day,
        "month": now.month
    }
    return pd.DataFrame([features])

if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Train the model first.")

    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully")
    print("Model expects features:", model.feature_names_in_)

    X_today = fetch_live_data()
    print("Input data columns:", list(X_today.columns))

    missing_cols = [col for col in model.feature_names_in_ if col not in X_today.columns]
    extra_cols = [col for col in X_today.columns if col not in model.feature_names_in_]

    print("Missing columns in input data (will be added with 0):", missing_cols)
    print("Extra columns in input data (will be dropped):", extra_cols)

    for col in missing_cols:
        X_today[col] = 0.0

    X_today = X_today[[col for col in model.feature_names_in_]]

    # Fill any NaN values with 0 before prediction
    X_today.fillna(0, inplace=True)

    print("Final columns sent to model:", list(X_today.columns))

    prediction = model.predict(X_today)[0]
    print(f"[{datetime.now()}] Predicted AQI for {CITY}: {prediction:.2f}")

    os.makedirs(os.path.dirname(PREDICTIONS_FILE), exist_ok=True)
    df_pred = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "predicted_aqi": prediction
    }])
    if os.path.exists(PREDICTIONS_FILE):
        df_pred.to_csv(PREDICTIONS_FILE, mode="a", header=False, index=False)
    else:
        df_pred.to_csv(PREDICTIONS_FILE, index=False)
