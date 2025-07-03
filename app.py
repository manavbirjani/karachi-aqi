import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Karachi AQI", layout="centered")
st.title("🌫️ Karachi AQI Dashboard (Forecast-Based)")

prediction_file = "data/daily_predictions.csv"
if os.path.exists(prediction_file):
    df = pd.read_csv(prediction_file)
    df['prediction_time'] = pd.to_datetime(df['prediction_time'])
    latest = df.sort_values('prediction_time').iloc[-1]

    st.metric("📊 Latest Predicted AQI", f"{latest['aqi_predicted']:.2f}")
    st.line_chart(df.set_index('prediction_time')['aqi_predicted'])

    with st.expander("🗃️ Raw Predictions"):
        st.dataframe(df.tail(10))
else:
    st.warning("⚠️ No predictions found. Run predict_today.py first.")
