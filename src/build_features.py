import os
import pandas as pd

RAW_FILE = "data/daily_predictions.csv"
FEATURES_FILE = "data/features_karachi.csv"

def compute_and_append():
    if not os.path.exists(RAW_FILE):
        print(f"{RAW_FILE} not found.")
        return

    df = pd.read_csv(RAW_FILE)
    if df.empty:
        print("Raw CSV is empty.")
        return

    features_list = []

    for _, row in df.iterrows():
        # Safe datetime parsing
        ts = pd.to_datetime(row.get("prediction_time"), errors="coerce")
        if pd.isna(ts):
            print(f"Invalid datetime skipped: {row.get('prediction_time')}")
            continue

        # Safe AQI retrieval
        aqi_val = row.get("aqi_predicted", row.get("predicted_aqi", None))
        if pd.isna(aqi_val):
            print(f"Missing AQI skipped at {ts}")
            continue

        # Feature computation
        features = {
            "prediction_time": ts,
            "hour": ts.hour,
            "day_of_week": ts.dayofweek,
            "aqi_predicted": aqi_val,
            # add more features if needed
        }
        features_list.append(features)

    if not features_list:
        print("No valid features to append.")
        # Ensure empty CSV exists with correct columns
        if not os.path.exists(FEATURES_FILE):
            empty_df = pd.DataFrame(columns=["prediction_time", "hour", "day_of_week", "aqi_predicted"])
            empty_df.to_csv(FEATURES_FILE, index=False)
        return

    features_df = pd.DataFrame(features_list)

    # Append or create safely
    if os.path.exists(FEATURES_FILE):
        try:
            existing = pd.read_csv(FEATURES_FILE, parse_dates=["prediction_time"])
        except ValueError:
            print("prediction_time missing in existing CSV, creating empty DataFrame")
            existing = pd.DataFrame(columns=features_df.columns)
        combined = pd.concat([existing, features_df], ignore_index=True)
        combined.to_csv(FEATURES_FILE, index=False)
    else:
        features_df.to_csv(FEATURES_FILE, index=False)

    print(f"Features updated in {FEATURES_FILE}")

if __name__ == "__main__":
    compute_and_append()
