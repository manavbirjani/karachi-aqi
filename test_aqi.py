import requests, os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("AQI_API_TOKEN")
url = f"https://api.waqi.info/feed/Karachi/?token={API_TOKEN}"
response = requests.get(url)
print(response.json())
