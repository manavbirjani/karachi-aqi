import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import joblib

# === CONFIG ===
RAW_DATA_CSV = "data/raw_aqi_data_karachi.csv"
MODEL_PATH = "karachi_aqi_model.pkl"
VALIDATION_SPLIT = True  # Set False if no validation needed

# === STEP 1: Load historical data ===
df = pd.read_csv(RAW_DATA_CSV)

# === STEP 2: Ensure all required columns exist ===
required_cols = ['pm25', 'pm10', 'o3', 'co', 'no2', 'so2', 'hour', 'day', 'month', 'aqi_change', 'aqi']
for col in required_cols:
    if col not in df.columns:
        df[col] = 0.0  # placeholder if missing

# === STEP 3: Convert feature columns to numeric ===
X = df[['pm25','pm10','o3','co','no2','so2','hour','day','month','aqi_change']].apply(pd.to_numeric, errors='coerce')
y = pd.to_numeric(df['aqi'], errors='coerce')

# === STEP 4: Drop rows with NaN ===
X = X.dropna()
y = y[X.index]

# === STEP 5: Train model ===
if VALIDATION_SPLIT:
    # Split data into train and validation
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)
    
    # Calculate RMSE
    rmse_train = np.sqrt(mean_squared_error(y_train, y_train_pred))
    rmse_val = np.sqrt(mean_squared_error(y_val, y_val_pred))
    print(f"Training RMSE: {rmse_train:.2f}")
    print(f"Validation RMSE: {rmse_val:.2f}")
else:
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    print(f"Training RMSE: {rmse:.2f}")

# === STEP 6: Save trained model ===
joblib.dump(model, MODEL_PATH)
print(f"Model trained and saved as {MODEL_PATH}")
