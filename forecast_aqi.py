import os
import pandas as pd
import joblib
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("AQI_API_TOKEN")
CITY = "karachi"
MODEL_PATH = "models/karachi_aqi_model.pkl"
FORECAST_FILE = "data/forecast_predictions.csv"

def fetch_forecast_data():
    """Fetch next 3 days AQI forecast data from WAQI API."""
    if not API_TOKEN:
        raise ValueError("API token not found. Please set AQI_API_TOKEN in .env file.")

    url = f"https://api.waqi.info/forecast/{CITY}/?token={API_TOKEN}"
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(f"API request failed with status {response.status_code}")

    data = response.json()
    if data.get("status") != "ok":
        raise ValueError(f"API returned error: {data}")

    forecast_list = []
    now = datetime.now()

    for i in range(1, 4):  # next 3 days
        forecast_date = now + timedelta(days=i)
        forecast_list.append({
            "pm25": 0.0,  # API se available ho toh update karein
            "pm10": 0.0,
            "o3": 0.0,
            "co": 0.0,
            "no2": 0.0,
            "so2": 0.0,
            "hour": 12,  # fixed midday prediction
            "day": forecast_date.day,
            "month": forecast_date.month
        })

    return pd.DataFrame(forecast_list)

if __name__ == "__main__":
    # Load model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Train the model first.")

    model = joblib.load(MODEL_PATH)

    # Get forecast data
    forecast_df = fetch_forecast_data()

    # Align features
    missing_cols = [col for col in model.feature_names_in_ if col not in forecast_df.columns]
    for col in missing_cols:
        forecast_df[col] = 0.0

    forecast_df = forecast_df[model.feature_names_in_]

    # Predict
    predictions = model.predict(forecast_df)

    # Save predictions
    os.makedirs(os.path.dirname(FORECAST_FILE), exist_ok=True)
    results = []
    for i, pred in enumerate(predictions, 1):
        results.append({
            "timestamp": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
            "predicted_aqi": pred
        })

    df_results = pd.DataFrame(results)
    if os.path.exists(FORECAST_FILE):
        df_results.to_csv(FORECAST_FILE, mode="a", header=False, index=False)
    else:
        df_results.to_csv(FORECAST_FILE, index=False)

    print(f"Forecast for next 3 days saved to {FORECAST_FILE}")
