import os
import smtplib
from email.message import EmailMessage
import requests
import pandas as pd

DAILY_PRED = "data/daily_predictions.csv"
FORECAST_FILE = "data/forecast_3day.csv"

def load_latest(file_path, time_col):
    if not os.path.exists(file_path):
        print(f"{file_path} not found.")
        return None
    df = pd.read_csv(file_path, parse_dates=[time_col])
    if df.empty:
        return None
    df = df.sort_values(time_col)
    return df.iloc[-1]

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
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pwd)
        s.send_message(msg)
    print("Email sent to", to_addr)

def send_webhook(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Webhook status", r.status_code)
    except Exception as e:
        print("Webhook error:", e)

def check_threshold(aqi, time, source):
    threshold = float(os.getenv("ALERT_THRESHOLD", 200))
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
    # Daily prediction alert
    latest_daily = load_latest(DAILY_PRED, "prediction_time")
    if latest_daily is not None:
        aqi = float(latest_daily.get("aqi_predicted", latest_daily.get("predicted_aqi", 0)))
        check_threshold(aqi, latest_daily["prediction_time"], "Daily Prediction")

    # Forecast alert (next 3 days)
    forecast_df = pd.read_csv(FORECAST_FILE, parse_dates=["prediction_time"])
    for _, row in forecast_df.iterrows():
        check_threshold(float(row["predicted_aqi"]), row["prediction_time"], "3-Day Forecast")

if __name__ == "__main__":
    check_and_alert()
