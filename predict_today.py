import pandas as pd
import joblib
from fetch_data import fetch_aqi_data
from datetime import datetime
import os

CITY = "karachi"
TOKEN = "49ac32407e3a6bbf5332f84468ee1cb16ee550fd"

data = fetch_aqi_data(CITY, TOKEN)

if data:
    df = pd.DataFrame([data])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    df['day'] = df['datetime'].dt.day
    df['month'] = df['datetime'].dt.month

    X = df[['pm25', 'pm10', 'o3', 'hour', 'day', 'month']].fillna(0)

    print("🧾 Forecast-based AQI input features:")
    print(X)

    model_path = "models/karachi_aqi_model.pkl"
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}. Train it first using train_model.py.")
    else:
        model = joblib.load(model_path)
        prediction = model.predict(X)[0]
        print(f"📊 Predicted AQI for today: {prediction:.2f}")

        os.makedirs("data", exist_ok=True)
        prediction_log = pd.DataFrame([{
            'prediction_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'aqi_predicted': prediction
        }])
        prediction_log.to_csv(
            "data/daily_predictions.csv",
            mode='a',
            header=not os.path.exists("data/daily_predictions.csv"),
            index=False
        )
        print("✅ Prediction saved to data/daily_predictions.csv")
else:
    print("❌ Failed to fetch AQI forecast data.")
