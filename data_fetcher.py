import datetime
import requests
from cmems_sst import fetch_sst

# OpenWeather
import os

OPENWEATHER_API_KEY = os.getenv("openweathermap_key")

def get_weather(lat=15.5, lon=73.8):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    response = requests.get(url)
    data = response.json()

    weather = {
        "temperature": data["main"]["temp"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "wind_dir": data["wind"]["deg"],
        "visibility": data.get("visibility", 10000),  # fallback
        "weather_main": data["weather"][0]["main"],
    }

    return weather

def get_state_now(lat=15.5, lon=73.8):
    now = datetime.datetime.utcnow()
    today = now.date()

    # Weather
    weather = get_weather(lat, lon)

    # SST via CMEMS
    sst = fetch_sst(lat, lon, today - datetime.timedelta(days=2))  # 2-day lag

    # Return unified state object
    return {
        "datetime": now.isoformat(),
        "location": {"lat": lat, "lon": lon},
        "weather": weather,
        "sst": sst,
    }
