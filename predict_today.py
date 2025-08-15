import os
import requests
import pandas as pd
import joblib
from datetime import datetime

# === CONFIG ===
API_TOKEN = os.getenv("AQI_API_TOKEN")
MODEL_PATH = "karachi_aqi_model.pkl"
PREDICTION_CSV = "data/daily_predictions.csv"

# === STEP 1: Fetch live AQI data from WAQI API ===
data = None
if API_TOKEN:
    try:
        url = f"https://api.waqi.info/feed/karachi/?token={API_TOKEN}"
        response = requests.get(url).json()
        print("Raw API response:", response)
        if response.get("status") == "ok":
            data = response["data"]
        else:
            print("API returned error. Using fallback dummy data.")
    except Exception as e:
        print("API request failed:", e)

# Fallback dummy data
if data is None:
    data = {
        "aqi": 160,
        "iaqi": {
            "pm25": {"v": 160},
            "pm10": {"v": 120},
            "o3": {"v": 30},
            "co": {"v": 0.5},
            "no2": {"v": 20},
            "so2": {"v": 10}
        }
    }

# === STEP 2: Extract features ===
pm25 = data.get("iaqi", {}).get("pm25", {}).get("v", 0.0)
pm10 = data.get("iaqi", {}).get("pm10", {}).get("v", 0.0)
o3 = data.get("iaqi", {}).get("o3", {}).get("v", 0.0)
co = data.get("iaqi", {}).get("co", {}).get("v", 0.0)
no2 = data.get("iaqi", {}).get("no2", {}).get("v", 0.0)
so2 = data.get("iaqi", {}).get("so2", {}).get("v", 0.0)

now = datetime.now()
hour = now.hour
day = now.day
month = now.month

# AQI change calculation
try:
    df_prev = pd.read_csv(PREDICTION_CSV)
    last_aqi = df_prev["aqi_predicted"].iloc[-1]
    aqi_change = data.get("aqi", last_aqi) - last_aqi
except Exception:
    aqi_change = 0.0

# === STEP 3: Prepare features for model ===
X_new = pd.DataFrame([{
    "pm25": pm25,
    "pm10": pm10,
    "o3": o3,
    "co": co,
    "no2": no2,
    "so2": so2,
    "hour": hour,
    "day": day,
    "month": month,
    "aqi_change": aqi_change
}])
X_new = X_new.fillna(0.0)

# === STEP 4: Load trained model ===
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"{MODEL_PATH} not found! Run train_model.py first.")
model = joblib.load(MODEL_PATH)

# === STEP 5: Predict AQI ===
predicted_aqi = model.predict(X_new)[0]
print(f"Predicted AQI: {predicted_aqi:.2f} at {now}")

# === STEP 6: Append to CSV ===
new_row = {
    "prediction_time": now.isoformat(),  # ISO format for correct parsing
    "aqi_predicted": predicted_aqi,
    "pm25": pm25,
    "pm10": pm10,
    "o3": o3,
    "co": co,
    "no2": no2,
    "so2": so2,
    "hour": hour,
    "day": day,
    "month": month,
    "aqi": data.get("aqi", predicted_aqi),
    "aqi_change": aqi_change
}

try:
    df_store = pd.read_csv(PREDICTION_CSV)
    df_store = pd.concat([df_store, pd.DataFrame([new_row])], ignore_index=True)
except FileNotFoundError:
    df_store = pd.DataFrame([new_row])

df_store.to_csv(PREDICTION_CSV, index=False)
print("Prediction saved to CSV successfully!")
