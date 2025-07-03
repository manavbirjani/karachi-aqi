import os
import pandas as pd
from datetime import datetime
from fetch_data import fetch_aqi_data

CITY = "karachi"
TOKEN = "49ac32407e3a6bbf5332f84468ee1cb16ee550fd"  # Your API token

def fetch_and_append():
    data = fetch_aqi_data(CITY, TOKEN)
    if data:
        # Add the current fetch timestamp (regardless of API timestamp)
        data['fetched_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        df = pd.DataFrame([data])
        os.makedirs("data", exist_ok=True)
        file_path = "data/raw_aqi_data_karachi.csv"

        # Append to the CSV
        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, index=False)

        print(f"{data['fetched_at']} ✅ Data saved")
    else:
        print(datetime.now(), "❌ Fetch failed")

if __name__ == "__main__":
    fetch_and_append()
