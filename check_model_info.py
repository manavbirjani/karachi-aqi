import joblib

# Load model
model = joblib.load("models/karachi_aqi_model.pkl")
print("Model type:", type(model))

# Check which features were used in training
if hasattr(model, "feature_names_in_"):
    print("Features used in training:", model.feature_names_in_)

# Model parameters
print("\nModel parameters:")
print(model.get_params())
