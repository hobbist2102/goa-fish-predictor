import os
import datetime
import requests
from cmems_sst import fetch_sst

# Constants
LAT, LON = 15.5, 73.8  # Default location: Goa coast
WEATHER_KEY = os.getenv("openweathermap_key")

# ------------------------------------------------------------------
# Weather from OpenWeatherMap
# ------------------------------------------------------------------
def _fetch_weather(lat: float, lon: float):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        weather = {
            "temp": data["main"]["temp"],
            "wind": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", 10000) / 1000,  # convert to km
            "description": data["weather"][0]["description"].capitalize(),
        }
        return weather
    except Exception as e:
        print("⚠️ Error fetching weather:", e)
        return {}

# ------------------------------------------------------------------
# INCOIS Tides (Simulated placeholder)
# ------------------------------------------------------------------
def _fetch_tide_height():
    # Placeholder value — replace with INCOIS API integration
    import math
    now = datetime.datetime.utcnow()
    phase = (now.hour + now.minute / 60.0) / 24.0
    height = 1.5 + 1.0 * math.sin(2 * math.pi * phase)
    return round(height, 2)

# ------------------------------------------------------------------
# Aggregator
# ------------------------------------------------------------------
def get_state_now():
    today = datetime.date.today() - datetime.timedelta(days=2)  # CMEMS delay buffer

    weather = _fetch_weather(LAT, LON)
    tide_height = _fetch_tide_height()
    sst = fetch_sst(LAT, LON, today)

    return {
        "lat": LAT,
        "lon": LON,
        "date": today.isoformat(),
        "weather": weather,
        "tide_height": tide_height,
        "sst": sst,
    }
