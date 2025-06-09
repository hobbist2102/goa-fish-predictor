import os
import datetime
import requests

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


def _fetch_stormglass_data(lat, lon):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(hours=1)

    params = [
        "waveHeight", "waveDirection", "swellHeight", "swellDirection",
        "currentSpeed", "currentDirection", "visibility",
        "seaTemperature", "salinity", "oxygen", "chlorophyll",
        "seaLevel"
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
        }
    except Exception as e:
        print("⚠️ Stormglass fetch failed:", e)
        return {}


def get_state_now(lat=LAT, lon=LON):
    today = datetime.date.today()
    weather = _fetch_weather()
    stormglass = _fetch_stormglass_data(lat, lon)
    sst = fetch_sst(lat, lon, today)

    return {
        "datetime": datetime.datetime.now().isoformat(),
        "lat": lat,
        "lon": lon,
        "weather": weather,
        "stormglass": stormglass,
        "tide_height": stormglass.get("seaLevel"),
        "sst": sst
    }
