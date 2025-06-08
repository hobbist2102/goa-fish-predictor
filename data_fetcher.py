import os
import datetime
import requests
import json
import netCDF4 as nc
import numpy as np

LAT, LON = 15.5, 73.8  # Default location: Goa (Mormugao region)
WEATHER_KEY = os.getenv("openweathermap_key")
TIDE_KEY = os.getenv("worldtides_key")

# ----------------------------------------------------------------------
# Fetch current weather from OpenWeatherMap
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Fetch current tide height from WorldTides.info
# ----------------------------------------------------------------------
def _fetch_tide_height():
    url = f"https://www.worldtides.info/api/v2?heights&lat={LAT}&lon={LON}&key={TIDE_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if "heights" in data and data["heights"]:
            return round(data["heights"][0]["height"], 2)
        return None
    except Exception as e:
        print("⚠️ Tide fetch failed:", e)
        return None

# ----------------------------------------------------------------------
# Fetch SST from downloaded NetCDF file
# ----------------------------------------------------------------------
def fetch_sst(lat, lon, target_date):
    try:
        file_path = f"sst_{target_date.strftime('%Y%m%d')}.nc"
        ds = nc.Dataset(file_path)

        lats = ds.variables['latitude'][:]
        lons = ds.variables['longitude'][:]
        sst_data = ds.variables['analysed_sst'][0, :, :]

        lat_idx = (np.abs(lats - lat)).argmin()
        lon_idx = (np.abs(lons - lon)).argmin()
        sst_kelvin = sst_data[lat_idx, lon_idx]

        sst_celsius = round(sst_kelvin - 273.15, 2)
        ds.close()
        return sst_celsius
    except Exception as e:
        print("⚠️ SST fetch failed:", e)
        return None

# ----------------------------------------------------------------------
# Consolidate all state inputs
# ----------------------------------------------------------------------
def get_state_now():
    today = datetime.date.today() - datetime.timedelta(days=1)  # match with SST file timing
    weather = _fetch_weather()
    tide_height = _fetch_tide_height()
    sst = fetch_sst(LAT, LON, today)

    return {
        "datetime": datetime.datetime.now().isoformat(),
        "lat": LAT,
        "lon": LON,
        "weather": weather,
        "tide_height": tide_height,
        "sst": sst
    }
