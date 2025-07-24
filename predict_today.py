import requests
import pandas as pd
import joblib
import os
from datetime import datetime

# Load model
model = joblib.load("models/karachi_aqi_model.pkl")

# Get API token from environment variable
API_TOKEN = os.getenv("AQI_API_TOKEN")

if not API_TOKEN:
    raise ValueError("AQI_API_TOKEN not set in environment variables.")

# Fetch current AQI data for Karachi
url = f"https://api.waqi.info/feed/karachi/?token={API_TOKEN}"
response = requests.get(url)
data = response.json()

if data.get("status") != "ok":
    print("Failed to fetch AQI data:", data)
    exit(1)

# Extract required pollutant values
iaqi = data['data'].get('iaqi', {})
pm25 = iaqi.get('pm25', {}).get('v', 0)
pm10 = iaqi.get('pm10', {}).get('v', 0)
o3   = iaqi.get('o3', {}).get('v', 0)

# Time-based features
now = datetime.now()
hour = now.hour
day = now.day
month = now.month

# Prepare input features for the model
features = {
    'pm25': pm25,
    'pm10': pm10,
    'o3': o3,
    'hour': hour,
    'day': day,
    'month': month
}

# ⛔ Avoid emojis in print statements to prevent Unicode errors on Windows
print("Features for prediction:", features)

# Make prediction
df = pd.DataFrame([features])
predicted_aqi = model.predict(df)[0]
print(f"Predicted AQI: {predicted_aqi:.2f}")

# Save to CSV
prediction_df = pd.DataFrame([{
    "timestamp": now.isoformat(),
    "pm25": pm25,
    "pm10": pm10,
    "o3": o3,
    "hour": hour,
    "day": day,
    "month": month,
    "predicted_aqi": predicted_aqi
}])

csv_path = "data/daily_predictions.csv"
prediction_df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
print(f"Prediction saved to {csv_path}")
