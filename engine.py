import datetime
import math
import json
import os

from cmems_sst import fetch_sst

# Load species temperature preferences
with open("species.json", "r") as f:
    species_data = json.load(f)

# ------------------------------------------
# Utility functions
# ------------------------------------------

def clamp(val, min_val=0.0, max_val=1.0):
    return max(min(val, max_val), min_val)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

# ------------------------------------------
# Individual scoring functions
# ------------------------------------------

def tide_score(hrs_from_high):
    return sigmoid(-abs(hrs_from_high) / 1.5)

def solunar_score(period_type, mins_to_next):
    if period_type == "major":
        return 1.0
    elif period_type == "minor":
        return 0.7
    else:
        return math.exp(-mins_to_next / 90)

def light_score(solar_altitude, cloud_cover):
    base = clamp(1 - abs(solar_altitude) / 10, 0.3, 1.0)
    return clamp(base + 0.4 * cloud_cover)

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

def chlorophyll_score(chl):
    if chl < 0.1:
        return 0.2
    elif chl < 0.5:
        return 0.6
    elif chl < 1.5:
        return 0.9
    else:
        return 0.7

def oxygen_score(oxygen):
    if oxygen >= 6:
        return 1.0
    elif oxygen >= 4:
        return 0.8
    elif oxygen >= 2:
        return 0.5
    else:
        return 0.2

def salinity_score(salinity):
    return clamp(1 - abs(salinity - 35) / 5)

def swell_effect_score(direction, height):
    if height > 2:
        return 0.3
    elif height > 1:
        return 0.6
    else:
        return 0.9

def current_speed_score(speed):
    return clamp(math.exp(-abs(speed - 0.5)))

def depth_penalty(depth):
    return 1.0 if depth < 50 else 0.7

# ------------------------------------------
# Main prediction interface
# ------------------------------------------

def predict_best_catch(state):
    lat = state["lat"]
    lon = state["lon"]
    date = datetime.datetime.fromisoformat(state["datetime"]).date()

    results = []

    for species in species_data:
        score = (
            0.15 * tide_score(state["tide_hours_from_high"]) +
            0.10 * solunar_score(state["solunar_type"], state["solunar_mins_to_next"]) +
            0.10 * light_score(state["solar_altitude"], state["weather"]["clouds"] / 100) +
            0.10 * pressure_trend_score(state["weather"]["pressure"], state["pressure_6h_ago"]) +
            0.07 * wind_boost_score(state["weather"]["wind_speed"], state.get("is_onshore", True)) +
            0.08 * sst_score(state["sst"], species) +
            0.07 * seasonal_index(date.timetuple().tm_yday) +
            0.05 * chlorophyll_score(state.get("chlorophyll", 0.3)) +
            0.05 * oxygen_score(state.get("oxygen", 5.0)) +
            0.04 * salinity_score(state.get("salinity", 35.0)) +
            0.04 * swell_effect_score(state.get("swell_direction", 180), state.get("swell_height", 1.0)) +
            0.03 * current_speed_score(state.get("current_speed", 0.5)) +
            0.02 * depth_penalty(state.get("depth", 20.0))
        )

        results.append((species, round(score, 3)))

    best = sorted(results, key=lambda x: x[1], reverse=True)[0]
    return {
        "species": best[0],
        "score": best[1],
        "recommendation": "Use bait" if best[1] < 0.6 else "Try lure",
        "all_scores": results
    }
