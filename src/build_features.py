# src/build_features.py
"""
Compute features and append to data/features_store.csv

Input source: data/daily_predictions.csv
Output: data/features_store.csv (append)
Columns: timestamp, pm25, pm10, o3, hour, day, month, pm25_change
"""

import pandas as pd
import os

RAW_PRED = "data/daily_predictions.csv"
FEATURES_PATH = "data/features_store.csv"

def load_preds():
    if not os.path.exists(RAW_PRED):
        raise FileNotFoundError(f"{RAW_PRED} not found.")
    df = pd.read_csv(RAW_PRED, parse_dates=["prediction_time"])
    df = df.sort_values("prediction_time").reset_index(drop=True)
    return df

def compute_and_append():
    df = load_preds()
    if df.empty:
        print("No predictions to build features from.")
        return

    # take latest two rows to compute change -- if only one row, change=0
    rows = []
    for i in range(len(df)):
        row = df.iloc[i]
        prev_pm25 = df.iloc[i-1]["pm25"] if i-1 >= 0 else None
        pm25 = float(row.get("pm25", 0))
        pm10 = float(row.get("pm10", 0))
        o3 = float(row.get("o3", 0))
        ts = pd.to_datetime(row["prediction_time"])
        pm25_change = pm25 - (prev_pm25 if prev_pm25 is not None else pm25)
        rows.append({
            "timestamp": ts,
            "pm25": pm25,
            "pm10": pm10,
            "o3": o3,
            "hour": ts.hour,
            "day": ts.day,
            "month": ts.month,
            "pm25_change": pm25_change
        })

    feat_df = pd.DataFrame(rows)

    # Append only new rows that are not present in features_store (based on timestamp)
    if os.path.exists(FEATURES_PATH):
        existing = pd.read_csv(FEATURES_PATH, parse_dates=["timestamp"])
        new = feat_df[~feat_df["timestamp"].isin(existing["timestamp"])]
        if new.empty:
            print("No new feature rows to append.")
            return
        new.to_csv(FEATURES_PATH, mode="a", header=False, index=False)
        print(f"Appended {len(new)} rows to {FEATURES_PATH}")
    else:
        feat_df.to_csv(FEATURES_PATH, index=False)
        print(f"Created {FEATURES_PATH} with {len(feat_df)} rows")

if __name__ == "__main__":
    compute_and_append()
