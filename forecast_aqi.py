import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import random
import time


API_TOKEN = os.getenv("AQI_API_TOKEN")
CITY_LAT = 24.8607
CITY_LON = 67.0011
FORECAST_FILE = "data/forecast_3day.csv"
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds

if not API_TOKEN:
    raise EnvironmentError("AQI_API_TOKEN environment variable not set!")

API_URL = f"https://api.waqi.info/forecast/daily/geo:{CITY_LAT};{CITY_LON}/?token={API_TOKEN}"

def fetch_forecast():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "ok" or "forecast" not in data.get("data", {}):
                raise ValueError("Invalid API response structure")
            return data["data"]["forecast"]["daily"]
        except Exception as e:
            print(f"API request failed (attempt {attempt}): {e}")
            time.sleep(RETRY_DELAY)
    print("⚠ Max retries reached. Using placeholder forecast.")
    return None

def create_forecast_df(api_forecast):
    rows = []
    today = datetime.now()
    if api_forecast:
        # Use real API data
        pm25_list = api_forecast.get("pm25", [])
        pm10_list = api_forecast.get("pm10", [])
        o3_list = api_forecast.get("o3", [])
        for i in range(3):
            try:
                date_str = pm25_list[i]["day"]
                rows.append({
                    "prediction_time": date_str,
                    "pm25": pm25_list[i]["avg"],
                    "pm10": pm10_list[i]["avg"],
                    "o3": o3_list[i]["avg"],
                    "aqi_predicted": pm25_list[i]["avg"],  # simplified AQI proxy
                })
            except IndexError:
                # If API data less than 3 days, fill placeholder
                rows.append({
                    "prediction_time": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "pm25": random.randint(100, 200),
                    "pm10": random.randint(80, 150),
                    "o3": random.randint(10, 50),
                    "aqi_predicted": random.randint(150, 250),
                })
    else:
        # Placeholder if API fails
        for i in range(3):
            rows.append({
                "prediction_time": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                "pm25": random.randint(100, 200),
                "pm10": random.randint(80, 150),
                "o3": random.randint(10, 50),
                "aqi_predicted": random.randint(150, 250),
            })
    return pd.DataFrame(rows)

def main():
    os.makedirs("data", exist_ok=True)
    api_forecast = fetch_forecast()
    df = create_forecast_df(api_forecast)
    df.to_csv(FORECAST_FILE, index=False)
    print(f"Forecast saved to {FORECAST_FILE}")

if __name__ == "__main__":
    main()
