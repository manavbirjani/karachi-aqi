import requests
import pandas as pd
import joblib
from datetime import datetime
import os

# Config
CITY = "karachi"
TOKEN = "49ac32407e3a6bbf5332f84468ee1cb16ee550fd"  
MODEL_PATH = "models/karachi_aqi_model.pkl"
PREDICTION_FILE = "data/daily_predictions.csv"

# Step 1: Fetch API data
def fetch_aqi_data(city, token):
    url = f"https://api.waqi.info/feed/{city}/?token={token}"
    response = requests.get(url)
    return response.json()

# Step 2: Extract forecast feature values
def get_forecast_avg(data, key):
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        for entry in data['forecast']['daily'][key]:
            if entry['day'] == today:
                return entry['avg']
        return None
    except:
        return None

# Fetch data
api_response = fetch_aqi_data(CITY, TOKEN)

if api_response["status"] == "ok":
    data = api_response["data"]

    # Extract forecast-based features
    pm25 = get_forecast_avg(data, "pm25")
    pm10 = get_forecast_avg(data, "pm10")
    o3 = get_forecast_avg(data, "o3")
    hour = datetime.now().hour
    day = datetime.now().day
    month = datetime.now().month

    features = pd.DataFrame([{
        "pm25": pm25,
        "pm10": pm10,
        "o3": o3,
        "hour": hour,
        "day": day,
        "month": month
    }])

    # Step 3: Load the trained model
    model = joblib.load(MODEL_PATH)

    # Step 4: Predict AQI
    predicted_aqi = model.predict(features)[0]
    print("📊 Predicted AQI for today:", predicted_aqi)

    # Step 5: Save result
    prediction_entry = pd.DataFrame([{
        "predicted_aqi": predicted_aqi,
        "prediction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    # Create file if not exists
    if not os.path.exists(PREDICTION_FILE):
        prediction_entry.to_csv(PREDICTION_FILE, index=False)
    else:
        prediction_entry.to_csv(PREDICTION_FILE, mode='a', header=False, index=False)

    print("✅ Prediction saved to", PREDICTION_FILE)

else:
    print("❌ API Error:", api_response.get("data"))
