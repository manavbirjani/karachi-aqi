import os
import smtplib
from email.message import EmailMessage
import requests
import pandas as pd

# File paths
DAILY_PRED = "data/daily_predictions.csv"
FORECAST_FILE = "data/forecast_3day.csv"

def load_latest(file_path):
    """Load the latest row with valid AQI from CSV. Uses last row to ensure latest entry is picked."""
    if not os.path.exists(file_path):
        print(f"{file_path} not found.")
        return None

    df = pd.read_csv(file_path)

    # Determine AQI column
    aqi_col = "aqi_predicted" if "aqi_predicted" in df.columns else "predicted_aqi"
    if aqi_col not in df.columns:
        print(f"No AQI column found in {file_path}")
        return None

    # Keep only rows with valid AQI
    df_valid = df[df[aqi_col].notna()]
    if df_valid.empty:
        print("No valid AQI found in CSV")
        return None

    # Take the last row of the CSV (append-only assumption)
    latest_row = df_valid.tail(1).iloc[0]

    # Flexible datetime parsing
    try:
        latest_row["prediction_time"] = pd.to_datetime(latest_row["prediction_time"], errors="coerce")
    except:
        pass

    return latest_row

def send_email(subject, body, to_addr):
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    if not user or not pwd:
        print("SMTP creds not set. Skipping email.")
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(user, pwd)
            s.send_message(msg)
        print("Email sent to", to_addr)
    except Exception as e:
        print("Email sending failed:", e)

def send_webhook(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Webhook status", r.status_code)
    except Exception as e:
        print("Webhook error:", e)

def check_threshold(aqi, time, source):
    threshold = float(os.getenv("ALERT_THRESHOLD", 200))
    if pd.isna(aqi):
        print(f"AQI value missing for {source} at {time}")
        return
    if aqi >= threshold:
        subject = f"[ALERT] High AQI {aqi:.0f} ({source})"
        body = f"Predicted AQI: {aqi:.0f}\nTime: {time}\nSource: {source}\nPlease take action."
        to = os.getenv("ALERT_EMAIL_TO")
        if to:
            send_email(subject, body, to)
        webhook = os.getenv("ALERT_WEBHOOK_URL")
        if webhook:
            send_webhook(webhook, {"text": subject, "aqi": aqi, "time": str(time), "source": source})
        print(f"Alert triggered from {source}: {aqi}")
    else:
        print(f"AQI OK from {source}: {aqi}")

def check_and_alert():
    # --- Daily Prediction ---
    latest_daily = load_latest(DAILY_PRED)
    if latest_daily is not None:
        aqi_value = latest_daily.get("aqi_predicted", latest_daily.get("predicted_aqi", None))
        if pd.isna(aqi_value):
            print(f"AQI value missing for Daily Prediction at {latest_daily['prediction_time']}")
        else:
            check_threshold(float(aqi_value), latest_daily["prediction_time"], "Daily Prediction")

    # --- 3-Day Forecast ---
    if os.path.exists(FORECAST_FILE):
        forecast_df = pd.read_csv(FORECAST_FILE)
        if not forecast_df.empty:
            for _, row in forecast_df.iterrows():
                aqi_forecast = row.get("aqi_predicted", row.get("predicted_aqi", None))
                if pd.isna(aqi_forecast):
                    print(f"AQI value missing for 3-Day Forecast at {row['prediction_time']}")
                    continue
                # Flexible datetime parse
                try:
                    pred_time = pd.to_datetime(row["prediction_time"], errors="coerce")
                except:
                    pred_time = row["prediction_time"]
                check_threshold(float(aqi_forecast), pred_time, "3-Day Forecast")
        else:
            print(f"{FORECAST_FILE} is empty.")
    else:
        print(f"{FORECAST_FILE} not found.")

if __name__ == "__main__":
    check_and_alert()
