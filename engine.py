import datetime
import math
import json
import os

from cmems_sst import fetch_sst

# Load species temperature preferences
with open("species.json", "r") as f:
    species_data = json.load(f)

# --------------------------
# Utility Functions
# --------------------------

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def clamp(val, min_val=0.0, max_val=1.0):
    return max(min(val, max_val), min_val)

# --------------------------
# Scoring Components
# --------------------------

def tide_score(hours_from_high):
    return sigmoid(-abs(hours_from_high) / 1.5)

def solunar_score(period_type, mins_to_next):
    if period_type == "major":
        return 1.0
    elif period_type == "minor":
        return 0.7
    else:
        return math.exp(-mins_to_next / 90)

def light_score(solar_altitude_deg, cloud_fraction):
    base = clamp(1 - abs(solar_altitude_deg) / 10, 0.3, 1)
    return base + 0.4 * cloud_fraction

def pressure_trend_score(p_now, p_6h_ago):
    delta = p_now - p_6h_ago
    return clamp(0.5 + delta / 8)

def wind_boost_score(speed_mps, is_onshore):
    if speed_mps < 2:
        return 0.4
    elif 2 <= speed_mps <= 7:
        return 0.9 if is_onshore else 0.5
    else:
        return 0.3

def sst_score(current_sst, species_name):
    try:
        species = species_data[species_name]
        T_opt = species["preferred_temperature"]
        sigma = species.get("tolerance_sigma", 2)
        return math.exp(-((current_sst - T_opt) ** 2) / (2 * sigma ** 2))
    except KeyError:
        return 0.5

def seasonal_index(day_of_year, peak_day=288):
    return 0.5 + 0.5 * math.sin(2 * math.pi * (day_of_year - peak_day) / 365)

def method_bias(method, is_daytime):
    if (method == "lure" and is_daytime) or (method == "bait" and not is_daytime):
        return 0.1
    return 0.0

# --------------------------
# Master Prediction Function
# --------------------------

def compute_fish_score(
    species_name,
    lat,
    lon,
    date: datetime.date,
    hrs_from_high,
    daily_tide_range,
    max_range_30d,
    solunar_type,
    mins_to_solunar,
    solar_alt,
    cloud_frac,
    pressure_now,
    pressure_6h_ago,
    wind_speed,
    is_onshore,
    method,
    is_day
):
    sst = fetch_sst(lat, lon, date)
    if sst is None:
        sst = 27.0

    score = (
        0.25 * tide_score(hrs_from_high) +
        0.10 * (daily_tide_range / max_range_30d) +
        0.20 * solunar_score(solunar_type, mins_to_solunar) +
        0.10 * light_score(solar_alt, cloud_frac) +
        0.10 * pressure_trend_score(pressure_now, pressure_6h_ago) +
        0.07 * wind_boost_score(wind_speed, is_onshore) +
        0.05 * sst_score(sst, species_name) +
        0.03 * 1.0 +  # Turbidity placeholder
        0.07 * seasonal_index(date.timetuple().tm_yday) +
        0.03 * method_bias(method, is_day)
    )

    if score >= 0.80:
        label = "Excellent"
    elif score >= 0.65:
        label = "Good"
    elif score >= 0.50:
        label = "Fair"
    else:
        label = "Poor"

    return round(score, 3), label, round(sst, 2)

# --------------------------
# Simple wrapper for current use
# --------------------------

def calc_fai(state):
    return compute_fish_score(
        species_name="snapper",
        lat=state["lat"],
        lon=state["lon"],
        date=datetime.date.today(),
        hrs_from_high=0.5,
        daily_tide_range=1.3,
        max_range_30d=2.4,
        solunar_type="major",
        mins_to_solunar=20,
        solar_alt=8,
        cloud_frac=state["weather"].get("clouds", 20) / 100,
        pressure_now=state["weather"].get("pressure", 1012),
        pressure_6h_ago=state["weather"].get("pressure", 1010),
        wind_speed=state["weather"].get("wind_speed", 2),
        is_onshore=True,
        method="lure",
        is_day=True
    )
