# predict_today.py (replace)
import os
import joblib
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("AQI_API_TOKEN")
MODEL_PATH = "models/karachi_aqi_model.pkl"
OUT_PATH = "data/daily_predictions.csv"

# default feature ordering used in training
DEFAULT_FEATURES = ["pm25", "pm10", "o3", "co", "no2", "so2", "hour", "day", "month", "pm25_change"]

def fetch_live_data():
    if not API_TOKEN:
        raise RuntimeError("AQI_API_TOKEN not set in environment variables.")
    url = f"https://api.waqi.info/feed/karachi/?token={API_TOKEN}"
    r = requests.get(url, timeout=10)
    data = r.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"API returned error: {data}")
    iaqi = data["data"].get("iaqi", {})
    def val(k): return float(iaqi.get(k, {}).get("v", 0.0))
    now = datetime.now()
    # try to compute pm25_change using last features if available
    pm25_change = 0.0
    # Build dict
    row = {
        "pm25": val("pm25"),
        "pm10": val("pm10"),
        "o3": val("o3"),
        "co": val("co"),
        "no2": val("no2"),
        "so2": val("so2"),
        "hour": now.hour,
        "day": now.day,
        "month": now.month,
        "pm25_change": pm25_change
    }
    return pd.DataFrame([row]), now

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_model.py")
    return joblib.load(MODEL_PATH)

def align_features(df, model):
    # get feature names expected by model
    if hasattr(model, "feature_names_in_"):
        feature_names = list(model.feature_names_in_)
    else:
        feature_names = DEFAULT_FEATURES
    # add missing cols with zeros and drop extras
    for c in feature_names:
        if c not in df.columns:
            df[c] = 0.0
    df = df[feature_names]
    return df, feature_names

def append_prediction(ts, pred):
    os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)
    row = {"prediction_time": ts.strftime("%Y-%m-%d %H:%M:%S"), "aqi_predicted": float(pred)}
    df_out = pd.DataFrame([row])
    if os.path.exists(OUT_PATH):
        df_out.to_csv(OUT_PATH, mode="a", header=False, index=False)
    else:
        df_out.to_csv(OUT_PATH, index=False)

if __name__ == "__main__":
    df_feat, ts = fetch_live_data()
    model = load_model()
    df_aligned, feat_names = align_features(df_feat, model)
    pred = model.predict(df_aligned)[0]
    append_prediction(ts, pred)
    print(f"Predicted AQI: {pred:.2f} at {ts}")
