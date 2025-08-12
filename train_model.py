# train_model.py  (replace your file with this)
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from datetime import datetime

FEATURES_PATH = "data/features_store.csv"
MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "karachi_aqi_model.pkl")

def train_model():
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"{FEATURES_PATH} not found. Run build_features.py first.")

    df = pd.read_csv(FEATURES_PATH, parse_dates=["timestamp"], dayfirst=False)
    print(f"Loaded {len(df)} rows from {FEATURES_PATH}")

    # choose target: prefer 'aqi', else fallback to 'pm25'
    target_col = "aqi" if "aqi" in df.columns else "pm25"
    if "aqi" not in df.columns:
        print("WARNING: 'aqi' column not found. Using 'pm25' as target instead.")

    df = df.dropna(subset=[target_col])
    if df.empty:
        raise ValueError(f"No rows left after dropping NaN from '{target_col}'.")

    X = df.drop(columns=["timestamp", target_col], errors="ignore").fillna(0)
    y = df[target_col]

    # simple train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5

    os.makedirs(MODELS_DIR, exist_ok=True)
    # overwrite stable filename so CI always finds the same path
    joblib.dump(model, MODEL_PATH, compress=3)

    print(f"Model saved to {MODEL_PATH}")
    print(f"Model Trained | RMSE: {rmse:.3f}")

if __name__ == "__main__":
    train_model()
