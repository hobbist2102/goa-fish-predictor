import requests
from datetime import datetime
import pytz
import os

from cmems_sst import fetch_sst
from incois_tide import get_tide_height

# Load OWM API key
OWM_KEY = os.getenv("openweathermap_key")

# Default coords (Goa center)
DEFAULT_LAT = 15.5
DEFAULT_LON = 73.8

def _fetch_weather(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}"
        f"&exclude=minutely,daily,alerts&appid={OWM_KEY}&units=metric"
    )

    res = requests.get(url)
    data = res.json()

    now = datetime.utcnow()
    hourly = data["hourly"]
    idx_now = min(range(len(hourly)), key=lambda i: abs(hourly[i]["dt"] - now.timestamp()))
    current = hourly[idx_now]

    return {
        "time": datetime.utcfromtimestamp(current["dt"]).astimezone(pytz.timezone("Asia/Kolkata")),
        "temp": current["temp"],
        "wind_speed": current["wind_speed"],
        "wind_deg": current["wind_deg"],
        "pressure": current["pressure"],
        "clouds": current["clouds"],
        "visibility": current.get("visibility", 10000)
    }

def _fetch_moon_phase():
    # Moon phase is approximated using phase angle calc
    day_of_cycle = (datetime.utcnow() - datetime(2001, 1, 1)).days % 29.53
    if day_of_cycle < 1 or day_of_cycle > 28.5:
        return "new"
    elif 13.5 < day_of_cycle < 16.5:
        return "full"
    elif day_of_cycle < 13.5:
        return "waxing"
    else:
        return "waning"

def get_state_now(lat=DEFAULT_LAT, lon=DEFAULT_LON):
    weather = _fetch_weather(lat, lon)
    moon = _fetch_moon_phase()
    tide_height = get_tide_height(weather["time"].time()) or 0.0
    sst = fetch_sst() or 27.0

    return {
        "datetime": weather["time"],
        "temp_c": weather["temp"],
        "pressure_hPa": weather["pressure"],
        "wind_kph": weather["wind_speed"] * 3.6,
        "wind_deg": weather["wind_deg"],
        "cloud_pct": weather["clouds"],
        "visibility_m": weather["visibility"],
        "moon_phase": moon,
        "tide_m": tide_height,
        "sst_c": sst
    }
