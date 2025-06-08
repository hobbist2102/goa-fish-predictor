import requests
from datetime import datetime, timedelta
import pytz

# -------------------- CONSTANTS --------------------

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"
API_KEY = st.secrets["openweathermap_key"]  # read from secrets.toml

# -------------------- MAIN FUNCTION --------------------

def get_state_now(lat: float, lon: float, target_time: datetime = None):
    """
    Fetches live weather forecast and builds a unified state snapshot for predictions.
    If no time is given, defaults to current UTC+5:30.
    """

    if not target_time:
        target_time = datetime.now(pytz.timezone("Asia/Kolkata"))

    weather = _fetch_weather(lat, lon, target_time)

    state = {
        "lat": lat,
        "lon": lon,
        "timestamp": target_time.isoformat(),
        "temp_c": weather["temp_c"],
        "wind_kph": weather["wind_kph"],
        "pressure_hpa": weather["pressure_hpa"],
        "visibility_km": weather["visibility_km"],
        "cloud_pct": weather["cloud_pct"],
        "moon_phase": _estimate_moon_phase(target_time),
        "hour": target_time.hour,
        "month": target_time.month
    }

    return state

# -------------------- WEATHER HELPER --------------------

def _fetch_weather(lat, lon, target_time):
    """
    Get weather forecast for the given coordinates and time from OpenWeatherMap.
    Matches nearest available hour in forecast block.
    """

    response = requests.get(OPENWEATHER_URL, params={
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    })

    if response.status_code != 200:
        raise RuntimeError("Failed to fetch weather data")

    data = response.json()
    hourly = data.get("list", [])

    # Find closest forecast to requested time
    target_str = target_time.strftime("%Y-%m-%d %H:00:00")
    closest = min(hourly, key=lambda x: abs(datetime.strptime(x["dt_txt"], "%Y-%m-%d %H:%M:%S") - target_time))

    return {
        "temp_c": closest["main"]["temp"],
        "pressure_hpa": closest["main"]["pressure"],
        "wind_kph": closest["wind"]["speed"] * 3.6,
        "cloud_pct": closest["clouds"]["all"],
        "visibility_km": (closest.get("visibility", 10000)) / 1000  # meters to km
    }

# -------------------- MOON PHASE ESTIMATION --------------------

def _estimate_moon_phase(dt: datetime) -> float:
    """
    Approximate moon phase as a float between 0 (New Moon) and 1 (Full Moon).
    Uses a simplified astronomical calculation.
    """
    known_new_moon = datetime(2001, 1, 1, 0, 0, 0)
    synodic_month = 29.53058867
    days = (dt - known_new_moon).days + (dt - known_new_moon).seconds / 86400
    phase = days % synodic_month
    return abs((phase / synodic_month) - 0.5) * 2  # 0 = new, 1 = full
