import streamlit as st
import pandas as pd

# Load predictions
try:
    df = pd.read_csv("data/daily_predictions.csv")

    # Handle mixed datetime formats
    df['prediction_time'] = pd.to_datetime(df['prediction_time'], errors='coerce')

    if 'predicted_aqi' in df.columns and not df['predicted_aqi'].isnull().all():
        latest = df.sort_values("prediction_time").iloc[-1]
        st.title("🌫️ Karachi AQI Dashboard (Forecast-Based)")
        st.metric("📊 Latest Predicted AQI", f"{latest['predicted_aqi']:.0f}")
        st.write(f"🕒 Time: {latest['prediction_time']}")
    else:
        st.warning("No valid AQI prediction found.")
except Exception as e:
    st.error(f"Failed to load predictions: {e}")
