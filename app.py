import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Karachi AQI Dashboard", layout="centered")
st.title("🌫️ Karachi AQI Dashboard (Forecast-Based)")

file_path = "data/daily_predictions.csv"

if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path)

        # Drop unnecessary index column if it exists
        if "Unnamed: 0" in df.columns:
            df.drop(columns=["Unnamed: 0"], inplace=True)

        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]

        # Rename expected columns
        df.rename(columns={
            "prediction_time": "timestamp",
            "aqi_predicted": "predicted_aqi"
        }, inplace=True)

        # Ensure required columns exist
        if "timestamp" in df.columns and "predicted_aqi" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df["predicted_aqi"] = pd.to_numeric(df["predicted_aqi"], errors="coerce")
            df.dropna(subset=["timestamp", "predicted_aqi"], inplace=True)

            if not df.empty:
                # Sort and get latest
                df.sort_values("timestamp", ascending=False, inplace=True)
                latest = df.iloc[0]

                st.metric("📊 Latest Predicted AQI", f"{latest['predicted_aqi']:.2f}")
                st.text(f"🕒 Time: {latest['timestamp']}")

                # Plot only if there's valid data
                chart_df = df[["timestamp", "predicted_aqi"]].dropna()
                chart_df.set_index("timestamp", inplace=True)

                if not chart_df.empty:
                    st.subheader("📈 AQI Trend Over Time")
                    st.line_chart(chart_df)
                else:
                    st.warning("⚠️ No valid data for plotting.")
            else:
                st.warning("📉 No valid AQI predictions found in the CSV.")
        else:
            st.error("❌ Missing required columns: 'prediction_time' and 'aqi_predicted'")
            st.write("Found columns:", df.columns.tolist())

    except Exception as e:
        st.error(f"⚠️ Error reading prediction file: {e}")
else:
    st.warning("🚫 File not found: data/daily_predictions.csv")
