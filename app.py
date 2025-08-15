import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import os

st.set_page_config(page_title="Karachi AQI Dashboard", layout="centered")
st.title("🌫️ Karachi AQI Dashboard (Forecast-Based)")

# --- Paths ---
daily_csv = "data/daily_predictions.csv"
forecast_csv = "data/forecast_3day.csv"
prediction_script = "predict_today.py"

# --- Run prediction script ---
if os.path.exists(prediction_script):
    subprocess.run(["python", prediction_script], check=True)

# --- Latest AQI ---
st.subheader("📊 Latest Predicted AQI")
if os.path.exists(daily_csv):
    df = pd.read_csv(daily_csv)
    df['prediction_time'] = pd.to_datetime(df['prediction_time'], errors='coerce')
    df = df.drop_duplicates(subset=['prediction_time'], keep='last')
    
    if not df.empty:
        latest = df.sort_values("prediction_time", ascending=False).iloc[0]
        st.metric(label="AQI", value=f"{latest['aqi_predicted']:.2f}")
        st.caption(f"🕒 Time: {latest['prediction_time']}")
    else:
        st.warning("⚠️ No prediction data available.")
else:
    st.warning("⚠️ daily_predictions.csv not found.")

# --- 3-Day Forecast ---
st.subheader("📈 3-Day AQI Forecast")
if os.path.exists(forecast_csv):
    forecast_df = pd.read_csv(forecast_csv)
    forecast_df['prediction_time'] = pd.to_datetime(forecast_df['prediction_time'], errors='coerce')
    forecast_df = forecast_df.sort_values("prediction_time")
    
    if not forecast_df.empty:
        fig = px.line(
            forecast_df,
            x="prediction_time",
            y="aqi_predicted",
            title="📅 Forecasted AQI for Next 3 Days",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Forecast CSV is empty!")
else:
    st.warning("⚠️ Forecast CSV not found.")

# --- Auto-refresh ---
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=60*1000, key="datarefresh")
