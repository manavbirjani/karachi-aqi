import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Karachi AQI Forecast", layout="centered")

st.title("🌫️ Karachi AQI Dashboard (Forecast-Based)")

# Load the latest predicted AQI
try:
    df = pd.read_csv("data/daily_predictions.csv", parse_dates=["prediction_time"])
    latest = df.sort_values("prediction_time", ascending=False).iloc[0]
    
    st.subheader("📊 Latest Predicted AQI")
    st.metric(label="AQI", value=f"{latest['aqi_predicted']:.2f}")
    st.caption(f"🕒 Time: {latest['prediction_time']}")
except Exception as e:
    st.warning(f"⚠️ Error reading prediction file: {e}")

# Load the 3-day forecast data
st.subheader("📈 3-Day AQI Forecast")

forecast_file = "data/forecast_3day.csv"
if os.path.exists(forecast_file):
    try:
        forecast_df = pd.read_csv(forecast_file, parse_dates=["prediction_time"])
        forecast_df = forecast_df.sort_values("prediction_time")
        fig = px.line(
            forecast_df,
            x="prediction_time",
            y="predicted_aqi",
            title="📅 Forecasted AQI for Next 3 Days",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Error reading forecast file: {e}")
else:
    st.warning("⚠️ Forecast file not found. Please run forecast pipeline.")
