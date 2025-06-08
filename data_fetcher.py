import requests
from datetime import datetime, timedelta
import pytz
import math
import streamlit as st

# -------------------- CONSTANTS --------------------

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"
API_KEY = st.secrets["openweathermap_key"]
CMEMS_USER = st.secrets.get("CMEMS_USER")
CMEMS_PASS = st.secrets.get("CMEMS_PASS")
LAT = 15.5
LON = 73.8

# -------------------- MAIN ENTRY --------------------

def get_state(target_time: datetime):
    weather = _fetch_weather(LAT, LON, target_time)
    tide_height = _fetch_incois_tide(target_time)
    sst = _fetch_cmems_sst(target_time) or weather["temp_c"]

    return {
        "lat": LAT,
        "lon": LON,
        "timestamp": target_time.isoformat(),
        "temp_c": sst,
        "wind_kph": weather["wind_kph"],
        "pressure_hpa": weather["pressure_hpa"],
        "visibility_km": weather["visibility_km"],
        "cloud_pct": weather["cloud_pct"],
        "moon_phase": _estimate_moon_phase(target_time),
        "tide_m": tide_height,
        "hour": target_time.hour,
        "month": target_time.month
    }

# -------------------- WEATHER --------------------

def _fetch_weather(lat, lon, target_time):
    response = requests.get(OPENWEATHER_URL, params={
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    })
    response.raise_for_status()

    data = response.json()
    hourly = data.get("list", [])
    closest = min(hourly, key=lambda x: abs(datetime.strptime(x["dt_txt"], "%Y-%m-%d %H:%M:%S") - target_time))

    return {
        "temp_c": closest["main"]["temp"],
        "wind_kph": closest["wind"]["speed"] * 3.6,
        "pressure_hpa": closest["main"]["pressure"],
        "visibility_km": closest.get("visibility", 10000) / 1000,
        "cloud_pct": closest["clouds"]["all"]
    }

# -------------------- MOON PHASE --------------------

def _estimate_moon_phase(dt):
    year, month, day = dt.year, dt.month, dt.day
    if month < 3:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
    days_since_new = jd - 2451549.5
    new_moons = days_since_new / 29.53
    return round((new_moons - int(new_moons)) * 100, 2)  # percent illumination proxy

# -------------------- INCOIS TIDE (SCRAPED FALLBACK) --------------------

def _fetch_incois_tide(target_time):
    try:
        url = "https://webapps.incois.gov.in/TideForecast/"
        # In production, scrape page or download daily CSV if available (to be implemented)
        return 1.2  # placeholder fallback
    except:
        return 1.0

# -------------------- CMEMS SST --------------------

def _fetch_cmems_sst(target_time):
    if not CMEMS_USER or not CMEMS_PASS:
        return None

    try:
        # Example placeholder — Replace with CMEMS API or motuclient logic
        # This would normally request NetCDF data and extract SST for the lat/lon
        return 27.5  # placeholder fallback
    except:
        return None
