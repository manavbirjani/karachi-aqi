import os
import requests
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
WAQI_API_TOKEN = os.getenv("AQI_API_TOKEN")
if not WAQI_API_TOKEN:
    raise Exception("AQI_API_TOKEN environment variable is not set!")

MODEL_PATH = "karachi_aqi_model.pkl"
model = joblib.load(MODEL_PATH)

API_URL = f"https://api.waqi.info/feed/karachi/?token={WAQI_API_TOKEN}"
response = requests.get(API_URL)
data = response.json()
if data.get("status") != "ok":
    raise Exception("Failed to fetch AQI data!")

iaqi = data["data"].get("iaqi", {})
forecast = data["data"].get("forecast", {}).get("daily", {})
actual_aqi = data["data"].get("aqi", 0)
today_str = datetime.now().strftime("%Y-%m-%d")

def get_pollutant(name):
    value = iaqi.get(name, {}).get("v")
    if value is None and name in forecast:
        for f in forecast[name]:
            if f["day"] == today_str:
                value = f["avg"]
                break
    return value if value is not None else 0

features = {
    "pm25": get_pollutant("pm25"),
    "pm10": get_pollutant("pm10"),
    "o3": get_pollutant("o3"),
    "co": get_pollutant("co"),
    "no2": get_pollutant("no2"),
    "so2": get_pollutant("so2"),
    "hour": datetime.now().hour,
    "day": datetime.now().day,
    "month": datetime.now().month,
}

X_new = pd.DataFrame([features])
for col in model.feature_names_in_:
    if col not in X_new.columns:
        X_new[col] = 0
X_new = X_new[model.feature_names_in_]

aqi_predicted = model.predict(X_new)[0]

# --- Add small random noise (±2%) ---
noise = np.random.uniform(-0.02, 0.02) * aqi_predicted
aqi_predicted = aqi_predicted + noise

print(f"Predicted AQI (with noise): {aqi_predicted:.2f} at {datetime.now()}")

df_new = pd.DataFrame([{
    "prediction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "aqi_predicted": round(aqi_predicted, 2),   # <-- name changed
    **features,
    "aqi": actual_aqi,
    "aqi_change": round(aqi_predicted - actual_aqi, 2)
}])

csv_file = os.path.join("data", "daily_predictions.csv")
if os.path.exists(csv_file):
    df_existing = pd.read_csv(csv_file)
    df_all = pd.concat([df_existing, df_new], ignore_index=True)
else:
    df_all = df_new

df_all.to_csv(csv_file, index=False)
print("Prediction saved successfully (with noise)!")
