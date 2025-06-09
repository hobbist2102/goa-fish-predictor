import os
import datetime
import requests
import math

from cmems_sst import fetch_sst

LAT, LON = 15.5, 73.8
WEATHER_KEY = os.getenv("openweathermap_key")
STORMGLASS_KEY = os.getenv("stormglass_key")

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
            "wind_deg": data["wind"].get("deg", 0),
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility", 10000),
            "time": datetime.datetime.utcfromtimestamp(data["dt"]).isoformat()
        }
    except Exception as e:
        print("⚠️ Weather fetch failed:", e)
        return {}

def _fetch_pressure_6h_ago():
    url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={LAT}&lon={LON}&dt={int((datetime.datetime.utcnow() - datetime.timedelta(hours=6)).timestamp())}&appid={WEATHER_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data["current"]["pressure"]
    except Exception as e:
        print("⚠️ Pressure 6h ago fetch failed:", e)
        return None

def _fetch_stormglass_data(lat, lon):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(hours=1)

    params = [
        "waveHeight", "waveDirection", "swellHeight", "swellDirection",
        "currentSpeed", "currentDirection", "visibility",
        "seaTemperature", "salinity", "oxygen", "chlorophyll",
        "seaLevel", "seaFloorDepth"
    ]

    url = (
        f"https://api.stormglass.io/v2/weather/point"
        f"?lat={lat}&lng={lon}&params={','.join(params)}"
        f"&start={start.isoformat()}&end={end.isoformat()}"
    )

    headers = {"Authorization": STORMGLASS_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()["hours"][0]
        return {
            "waveHeight": data["waveHeight"]["noaa"],
            "waveDirection": data["waveDirection"]["noaa"],
            "swellHeight": data["swellHeight"]["noaa"],
            "swellDirection": data["swellDirection"]["noaa"],
            "currentSpeed": data["currentSpeed"]["noaa"],
            "currentDirection": data["currentDirection"]["noaa"],
            "visibility": data["visibility"]["noaa"],
            "salinity": data.get("salinity", {}).get("noaa"),
            "oxygen": data.get("oxygen", {}).get("noaa"),
            "chlorophyll": data.get("chlorophyll", {}).get("noaa"),
            "seaLevel": data.get("seaLevel", {}).get("noaa"),
            "depth": data.get("seaFloorDepth", {}).get("noaa")
        }
    except Exception as e:
        print("⚠️ Stormglass fetch failed:", e)
        return {}

def _approx_solar_altitude():
    now = datetime.datetime.utcnow()
    hour_angle = abs(now.hour - 12)
    return max(0, 90 - hour_angle * 7)

def _estimate_solunar():
    now = datetime.datetime.utcnow()
    hour = now.hour
    if 5 <= hour <= 7 or 17 <= hour <= 19:
        return "major", 0
    elif 9 <= hour <= 11 or 13 <= hour <= 15:
        return "minor", 60
    else:
        return "none", 180

def _estimate_tide_hours_from_high():
    now = datetime.datetime.utcnow()
    hours_since_midnight = now.hour + now.minute / 60
    return round(math.sin(hours_since_midnight * math.pi / 6), 2)  # fake sinusoidal approx

def _is_onshore(wind_deg):
    return 180 <= wind_deg <= 360

def get_state_now(lat=LAT, lon=LON):
    today = datetime.date.today()
    weather = _fetch_weather()
    stormglass = _fetch_stormglass_data(lat, lon)
    sst = fetch_sst(lat, lon, today)
    solunar_type, solunar_mins = _estimate_solunar()
    pressure_6h = _fetch_pressure_6h_ago()

    return {
        "datetime": datetime.datetime.utcnow().isoformat(),
        "lat": lat,
        "lon": lon,
        "weather": weather,
        "sst": sst,
        "tide_height": stormglass.get("seaLevel"),
        "tide_hours_from_high": _estimate_tide_hours_from_high(),
        "solunar_type": solunar_type,
        "solunar_mins_to_next": solunar_mins,
        "solar_altitude": _approx_solar_altitude(),
        "pressure_6h_ago": pressure_6h,
        "is_onshore": _is_onshore(weather.get("wind_deg", 0)),
        "chlorophyll": stormglass.get("chlorophyll"),
        "oxygen": stormglass.get("oxygen"),
        "salinity": stormglass.get("salinity"),
        "swell_height": stormglass.get("swellHeight"),
        "swell_direction": stormglass.get("swellDirection"),
        "current_speed": stormglass.get("currentSpeed"),
        "depth": stormglass.get("depth")
    }
