import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Get token from environment or ask user
token = os.getenv("AQI_API_TOKEN")
if not token:
    print("AQI_API_TOKEN not found in environment variables.")
    token = input("Please enter your AQI API Token: ").strip()
    if token:
        # Save to .env for future use
        with open(".env", "a") as f:
            f.write(f"\nAQI_API_TOKEN={token}")
        os.environ["AQI_API_TOKEN"] = token
    else:
        raise EnvironmentError("AQI API Token is required to proceed.")

# API details
CITY = "Karachi"
BASE_URL = f"https://api.waqi.info/feed/{CITY}/?token={token}"

# Fetch AQI data
def fetch_aqi_data():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "ok":
            raise ValueError(f"API error: {data}")
        return data["data"]
    except Exception as e:
        print(f"Error fetching AQI data: {e}")
        return None

# Save forecast to CSV
def save_forecast(data):
    forecast_data = []
    now = datetime.now()
    for i in range(3):  # 3-day forecast
        date = now + timedelta(days=i)
        aqi_value = data.get("aqi", None)
        forecast_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "forecast_aqi": aqi_value
        })

    df = pd.DataFrame(forecast_data)
    os.makedirs("data", exist_ok=True)
    file_path = "data/forecast_3day.csv"
    df.to_csv(file_path, index=False)
    print(f"Forecast saved to {file_path}")

# Main script
if __name__ == "__main__":
    aqi_data = fetch_aqi_data()
    if aqi_data:
        save_forecast(aqi_data)
