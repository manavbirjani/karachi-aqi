import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# Load features
df = pd.read_csv("data/features_karachi.csv")

# ❌ Drop rows where AQI is missing
df = df.dropna(subset=['aqi'])

# ✅ Prepare training data
X = df[['pm25', 'pm10', 'o3', 'hour', 'day', 'month']].fillna(0)
y = df['aqi']

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, "models/karachi_aqi_model.pkl")
print("✅ Model trained and saved to models/karachi_aqi_model.pkl")
