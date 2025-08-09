# src/alerts.py
"""
Alerting utility. Call check_and_alert() regularly after predictions.
Requires:
  - ALERT_THRESHOLD (env, default 200)
  - ALERT_EMAIL_TO (env) and SMTP_USER, SMTP_PASS (optional) OR
  - ALERT_WEBHOOK_URL (env) for POST webhook
"""

import os
import smtplib
from email.message import EmailMessage
import requests
import pandas as pd

DAILY_PRED = "data/daily_predictions.csv"

def load_latest():
    df = pd.read_csv(DAILY_PRED, parse_dates=["prediction_time"])
    df = df.sort_values("prediction_time")
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

def check_and_alert():
    if not os.path.exists(DAILY_PRED):
        print("Prediction file not found.")
        return

    latest = load_latest()
    aqi = float(latest.get("aqi_predicted", latest.get("predicted_aqi", 0)))
    threshold = float(os.getenv("ALERT_THRESHOLD", 200))
    if aqi >= threshold:
        subject = f"[ALERT] High AQI {aqi:.0f}"
        body = f"Predicted AQI: {aqi:.0f}\nTime: {latest['prediction_time']}\nPlease take action."
        to = os.getenv("ALERT_EMAIL_TO")
        if to:
            send_email(subject, body, to)
        webhook = os.getenv("ALERT_WEBHOOK_URL")
        if webhook:
            send_webhook(webhook, {"text": subject, "aqi": aqi, "time": str(latest["prediction_time"])})
        print("Alert triggered:", aqi)
    else:
        print("AQI OK:", aqi)

if __name__ == "__main__":
    check_and_alert()
