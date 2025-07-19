import requests
import pandas as pd
import datetime
import joblib
import os
import json

# Constants
MODEL_PATH = "models/karachi_aqi_model.pkl"
OUTPUT_FILE = "data/daily_predictions.csv"
API_TOKEN = os.getenv("AQI_API_TOKEN")  # Secure token usage
CITY_URL = f"https://api.waqi.info/feed/karachi/?token={API_TOKEN}"

# Fetch data from API
response = requests.get(CITY_URL)

try:
    data = response.json()  # ✅ Proper JSON parsing
except json.JSONDecodeError:
    print("Error decoding JSON from API.")
    exit(1)

print("🔍 Raw API response:", data)

# Extract forecast data
forecast = data.get("data", {}).get("forecast", {}).get("daily", {})
pm25 = forecast.get("pm25", [{}])[2].get("avg", None)
pm10 = forecast.get("pm10", [{}])[2].get("avg", None)
o3 = forecast.get("o3", [{}])[2].get("avg", None)

now = datetime.datetime.now()
features = pd.DataFrame([{
    "pm25": pm25,
    "pm10": pm10,
    "o3": o3,
    "hour": now.hour,
    "day": now.day,
    "month": now.month
}])

print("🧾 Forecast-based AQI input features:\n", features)

# Load model and predict
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    prediction = model.predict(features)[0]
    features["predicted_aqi"] = prediction
    features["prediction_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
    print("✅ Prediction result:", prediction)

    # Save to CSV
    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_csv(OUTPUT_FILE)
        df = pd.concat([old_df, features], ignore_index=True)
    else:
        df = features

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"📁 Prediction saved to {OUTPUT_FILE}")
else:
    print(f"❌ Model not found at {MODEL_PATH}")
