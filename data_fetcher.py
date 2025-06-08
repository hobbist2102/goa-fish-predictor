import os
import datetime
import requests

from cmems_sst import fetch_sst

LAT, LON = 15.5, 73.8
WEATHER_KEY = os.getenv("openweathermap_key")

def _fetch_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={WEATHER_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return {
            "temp": data["main"]["temp"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility", 10000),
            "time": datetime.datetime.utcfromtimestamp(data["dt"]).isoformat()
        }
    except Exception as e:
        print("⚠️ Weather fetch failed:", e)
        return {}

def _fetch_tide_height():
    # Placeholder for real INCOIS or tide integration
    import math
    t = datetime.datetime.now().timestamp() / 3600
    return round(1.2 * math.sin(t * 0.5) + 1.2, 2)

def get_state_now():
    today = datetime.date.today()
    weather = _fetch_weather()
    tide_height = _fetch_tide_height()
    sst = fetch_sst(LAT, LON, today)
    return {
        "datetime": datetime.datetime.now().isoformat(),
        "lat": LAT, "lon": LON,
        "weather": weather,
        "tide_height": tide_height,
        "sst": sst
    }
