import os
import pandas as pd
import joblib
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("AQI_API_TOKEN")
CITY = "karachi"
MODEL_PATH = "models/karachi_aqi_model.pkl"
PREDICTIONS_FILE = "data/daily_predictions.csv"

def fetch_live_data():
    """Fetch live AQI data from WAQI API."""
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

    # Extract required features with defaults
    features = {
        "pm25": iaqi.get("pm25", {}).get("v", 0.0),
        "pm10": iaqi.get("pm10", {}).get("v", 0.0),
        "o3": iaqi.get("o3", {}).get("v", 0.0),
        "co": iaqi.get("co", {}).get("v", 0.0),
        "no2": iaqi.get("no2", {}).get("v", 0.0),
        "so2": iaqi.get("so2", {}).get("v", 0.0),
        "hour": now.hour,
        "day": now.day,
        "month": now.month
    }

    return pd.DataFrame([features])

if __name__ == "__main__":
    # Load model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Train the model first.")

    model = joblib.load(MODEL_PATH)

    # Get live data
    X_today = fetch_live_data()

    # Align features with model
    missing_cols = [col for col in model.feature_names_in_ if col not in X_today.columns]
    for col in missing_cols:
        X_today[col] = 0.0  # default fill

    # Drop extra columns not in model
    X_today = X_today[model.feature_names_in_]

    # Predict
    prediction = model.predict(X_today)[0]
    print(f"[{datetime.now()}] Predicted AQI for {CITY}: {prediction:.2f}")

    # Save prediction
    os.makedirs(os.path.dirname(PREDICTIONS_FILE), exist_ok=True)
    df_pred = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "predicted_aqi": prediction
    }])
    if os.path.exists(PREDICTIONS_FILE):
        df_pred.to_csv(PREDICTIONS_FILE, mode="a", header=False, index=False)
    else:
        df_pred.to_csv(PREDICTIONS_FILE, index=False)
