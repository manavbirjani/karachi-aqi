import requests
import pandas as pd
import pickle
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_TOKEN = os.getenv("AQI_API_TOKEN")
if not API_TOKEN:
    raise ValueError("AQI_API_TOKEN not set in environment variables.")

# Fetch AQI data from WAQI API for Karachi
url = f"https://api.waqi.info/feed/karachi/?token={API_TOKEN}"
response = requests.get(url)
data = response.json()

if data["status"] != "ok":
    raise ValueError("Failed to fetch AQI data")

iaqi = data["data"].get("iaqi", {})

# Extract features, fill missing with 0
def get_value(key):
    return iaqi.get(key, {}).get("v", 0.0)

features = {
    "pm25": get_value("pm25"),
    "pm10": get_value("pm10"),
    "o3": get_value("o3"),
    "co": get_value("co"),
    "no2": get_value("no2"),
    "so2": get_value("so2"),
}

# Add time features
now = datetime.now()
features["hour"] = now.hour
features["day"] = now.day
features["month"] = now.month

# Convert to DataFrame
df = pd.DataFrame([features])

# Load trained model
with open("models/karachi_aqi_model.pkl", "rb") as f:
    model = pickle.load(f)

# Predict AQI
prediction = model.predict(df)[0]

# Save prediction
output_file = "data/daily_predictions.csv"
row = {
    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
    "predicted_aqi": prediction
}
df_out = pd.DataFrame([row])

# Append to file or create it
if os.path.exists(output_file):
    df_out.to_csv(output_file, mode='a', header=False, index=False)
else:
    df_out.to_csv(output_file, index=False)

print(f"Predicted AQI: {prediction:.2f}")
