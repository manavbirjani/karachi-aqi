import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor

# Load the correct CSV file
df = pd.read_csv("data/raw_aqi_data_karachi.csv")

# Rename column "03" to "o3" if needed
df.rename(columns={"03": "o3"}, inplace=True)

# Rename "datetime" to "timestamp" for clarity and consistency
df.rename(columns={"datetime": "timestamp"}, inplace=True)

# Convert timestamp column safely (invalid rows will become NaT)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Drop rows with invalid timestamps
df.dropna(subset=["timestamp"], inplace=True)

# Fill missing pollutants with 0 if they don’t exist
for col in ["pm25", "pm10", "o3", "co", "no2", "so2"]:
    if col not in df.columns:
        df[col] = 0.0

# Extract time-based features
df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.day
df["month"] = df["timestamp"].dt.month

# Define input features and target
features = ["pm25", "pm10", "o3", "co", "no2", "so2", "hour", "day", "month"]
X = df[features]
y = df["aqi"]

# Train the model
model = RandomForestRegressor()
model.fit(X, y)

# Save the model
with open("models/karachi_aqi_model.pkl", "wb") as f:
    pickle.dump(model, f)

print(" Model trained successfully.")
