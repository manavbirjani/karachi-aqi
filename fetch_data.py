import requests
from datetime import datetime

def fetch_aqi_data(city, token):
    url = f"https://api.waqi.info/feed/{city}/?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            forecast = result["data"]["forecast"]["daily"]
            today = forecast["pm25"][2]  # Usually index 2 is today
            features = {
                "pm25": today["avg"],
                "pm10": forecast["pm10"][2]["avg"],
                "o3": forecast["o3"][2]["avg"],
                "datetime": datetime.now()
            }
            return features
    return None
