import streamlit as st
import pandas as pd
import os

PREDICTION_FILE = "data/daily_predictions.csv"

st.set_page_config(page_title="Karachi AQI Dashboard", layout="centered")

st.title("🌫️ Karachi AQI Dashboard (Forecast-Based)")
st.markdown("This dashboard displays the **latest predicted Air Quality Index (AQI)** for Karachi based on forecasted pollutant levels.")

# Check if file exists
if not os.path.exists(PREDICTION_FILE):
    st.warning("No prediction data found yet.")
else:
    try:
        df = pd.read_csv(PREDICTION_FILE)
        
        # Convert time column
        df['prediction_time'] = pd.to_datetime(df['prediction_time'], errors='coerce')

        # Drop any rows with missing AQI
        df = df.dropna(subset=['predicted_aqi'])

        # Sort by time descending
        df = df.sort_values(by='prediction_time', ascending=False)

        latest = df.iloc[0]

        st.metric("📊 Latest Predicted AQI", f"{latest['predicted_aqi']:.2f}", help=str(latest['prediction_time']))

        # Optional: Show chart
        st.line_chart(df.set_index("prediction_time")["predicted_aqi"])

    except Exception as e:
        st.error(f"An error occurred: {e}")
