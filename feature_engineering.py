import requests

def fetch_aqi_data(city, token):
    url = f"https://api.waqi.info/feed/{city}/?token={token}"
    response = requests.get(url)
    data = response.json()

    print("🔍 Raw API response:", data)

    if data.get('status') == 'ok':
        forecast = data['data'].get('forecast', {}).get('daily', {})

        # Use forecast values instead of IAQI (more complete)
        pm25 = next((d.get('avg') for d in forecast.get('pm25', []) if d.get('day') == '2025-03-04'), None)
        pm10 = next((d.get('avg') for d in forecast.get('pm10', []) if d.get('day') == '2025-03-04'), None)
        o3 = next((d.get('avg') for d in forecast.get('o3', []) if d.get('day') == '2025-03-04'), None)

        return {
            'datetime': data['data']['time']['s'],
            'aqi': data['data']['aqi'],
            'pm25': pm25,
            'pm10': pm10,
            'co': None,
            'no2': None,
            'so2': None,
            'o3': o3,
        }

    return None
