import requests
import pandas as pd
import joblib
from datetime import datetime
import os

# Constants
API_TOKEN = os.getenv("AQI_API_TOKEN")  # Make sure this is set in your environment or .env file
API_URL = f"https://api.waqi.info/feed/karachi/?token={API_TOKEN}"
MODEL_PATH = "models/karachi_aqi_model.pkl"
PREDICTION_FILE = "data/daily_predictions.csv"

# Fetch AQI forecast data
response = requests.get(API_URL)
data = response.json()

# Parse forecast data
forecast = data.get("data", {}).get("forecast", {}).get("daily", {})

def get_avg(pollutant):
    try:
        return forecast[pollutant][2]['avg']
    except:
        return None

pm25 = get_avg("pm25")
pm10 = get_avg("pm10")
o3 = get_avg("o3")

# Prepare input features
now = datetime.now()
features = pd.DataFrame([{
    "pm25": pm25,
    "pm10": pm10,
    "o3": o3,
    "hour": now.hour,
    "day": now.day,
    "month": now.month
}])

# Check if data is valid
if features.isnull().any().any():
    print("⚠️ Missing input features, skipping prediction.")
    exit()

# Load model
model = joblib.load(MODEL_PATH)

# Make prediction
predicted_value = model.predict(features)[0]

# Save prediction
df = pd.DataFrame({
    "predicted_aqi": [predicted_value],
    "prediction_time": [now.strftime("%Y-%m-%d %H:%M:%S")]
})
df.to_csv(PREDICTION_FILE, index=False)
print(f"✅ Predicted AQI: {predicted_value:.2f}")
