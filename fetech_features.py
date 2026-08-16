import requests
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("AQI_API_TOKEN")
CITY = "Karachi"
FEATURES_PATH = "data/features_store.csv"

if not API_TOKEN:
    raise ValueError("API token not found. Please set AQI_API_TOKEN in your .env file.")

def fetch_aqi_data(city):
    url = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        raise Exception(f"API Error: {data}")

    aqi = data["data"]["aqi"]
    iaqi = data["data"]["iaqi"]

    pm25 = iaqi.get("pm25", {}).get("v", None)
    pm10 = iaqi.get("pm10", {}).get("v", None)
    o3 = iaqi.get("o3", {}).get("v", None)

    return {
        "timestamp": datetime.utcnow(),
        "aqi": aqi,
        "pm25": pm25,
        "pm10": pm10,
        "o3": o3
    }

# Always load old data if it exists, else start fresh
if os.path.exists(FEATURES_PATH):
    df = pd.read_csv(FEATURES_PATH)
else:
    df = pd.DataFrame(columns=["timestamp", "aqi", "pm25", "pm10", "o3"])

# Fetch new data
new_row = fetch_aqi_data(CITY)
df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

# Remove duplicates
df.drop_duplicates(subset=["timestamp"], inplace=True)

# Add time-based features
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.day
df["month"] = df["timestamp"].dt.month

# Add AQI change rate
df["aqi_change"] = df["aqi"].diff().fillna(0)

# Save to CSV
os.makedirs(os.path.dirname(FEATURES_PATH), exist_ok=True)
df.to_csv(FEATURES_PATH, index=False)

print(f"Features updated successfully! Total rows: {len(df)} | Columns: {list(df.columns)}")
