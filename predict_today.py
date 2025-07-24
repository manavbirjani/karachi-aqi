import requests
import pandas as pd
import joblib
from datetime import datetime

# Load model
model = joblib.load("models/karachi_aqi_model.pkl")

# Load token from environment variable (for GitHub Actions)
import os
API_TOKEN = os.getenv("AQI_API_TOKEN")

# Get current AQI data
url = f"https://api.waqi.info/feed/karachi/?token={API_TOKEN}"
response = requests.get(url)
data = response.json()

if data['status'] != 'ok':
    print("Failed to fetch AQI data:", data)
    exit(1)

# Extract values
iaqi = data['data'].get('iaqi', {})
pm25 = iaqi.get('pm25', {}).get('v', 0)
pm10 = iaqi.get('pm10', {}).get('v', 0)
o3 = iaqi.get('o3', {}).get('v', 0)

# Current datetime
now = datetime.now()
hour = now.hour
day = now.day
month = now.month

# Prepare features
features = {'pm25': pm25, 'pm10': pm10, 'o3': o3, 'hour': hour, 'day': day, 'month': month}
print("Features for prediction:", features)

df = pd.DataFrame([features])
predicted_aqi = model.predict(df)[0]
print(f"Predicted AQI: {predicted_aqi:.2f}")

# Save prediction
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

prediction_df.to_csv("data/daily_predictions.csv", mode='a', header=not os.path.exists("data/daily_predictions.csv"), index=False)
print("Prediction saved to data/daily_predictions.csv")
