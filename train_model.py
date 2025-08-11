
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from datetime import datetime

FEATURES_PATH = "data/features_store.csv"
MODELS_DIR = "models"

def train_model():
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"{FEATURES_PATH} not found. Run build_features.py first.")

    df = pd.read_csv(FEATURES_PATH)
    print(f"Loaded {len(df)} rows from {FEATURES_PATH}")

    # Choose target column
    target_col = "aqi" if "aqi" in df.columns else None
    if not target_col:
        print("⚠ Warning: 'aqi' column not found. Using pm25 as target instead.")
        target_col = "pm25"

    # Drop rows where target is NaN
    df = df.dropna(subset=[target_col])
    if df.empty:
        raise ValueError(f"No rows left after dropping NaN from target column '{target_col}'.")

    # Prepare features
    X = df.drop(columns=["timestamp", target_col], errors="ignore")
    y = df[target_col]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    # Predict & Calculate RMSE manually (for old sklearn)
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5

    # Save model with timestamp
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(
        MODELS_DIR,
        f"karachi_aqi_model-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pkl"
    )
    joblib.dump(model, model_path)

    print(f"Model saved to {model_path}")
    print(f"Model Trained | RMSE: {rmse:.2f}")

if __name__ == "__main__":
    train_model()
