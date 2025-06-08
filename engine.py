import math

def calc_fai(state: dict) -> float:
    """
    Compute Fish Activity Index (FAI) from live environmental state.
    Returns a float between 0.0 (dead) and 1.0 (perfect).
    """

    # ----------------------
    # Environmental variables
    # ----------------------
    wind_kph     = state["wind_kph"]
    pressure     = state["pressure_hpa"]
    moon         = state["moon_phase"]  # 0 = new moon, 1 = full moon
    hour         = state["hour"]
    month        = state["month"]
    visibility   = state["visibility_km"]
    cloud_pct    = state["cloud_pct"]

    # ----------------------
    # Scoring logic
    # ----------------------

    # Wind (best: 5–15 kph)
    if wind_kph < 3 or wind_kph > 25:
        wind_score = 0.2
    elif 5 <= wind_kph <= 15:
        wind_score = 1.0
    else:
        wind_score = 0.6

    # Pressure: most fish dislike sudden drops
    if pressure > 1018:
        pressure_score = 0.8
    elif 1010 <= pressure <= 1018:
        pressure_score = 1.0
    elif 1005 <= pressure < 1010:
        pressure_score = 0.6
    else:
        pressure_score = 0.3

    # Moon: strongest bite on full and new moon
    moon_score = 1.0 - abs(moon - 0.5) * 2  # Bell curve: 1.0 at 0 or 1, 0 at 0.5

    # Time of day: peaks around sunrise/sunset (5–8AM and 4–7PM)
    if 5 <= hour <= 8 or 16 <= hour <= 19:
        time_score = 1.0
    elif 9 <= hour <= 15:
        time_score = 0.6
    else:
        time_score = 0.3

    # Seasonality (simplified): higher score in monsoon-to-winter transition
    if month in [9, 10, 11, 12, 1, 2]:
        season_score = 1.0
    elif month in [6, 7, 8]:
        season_score = 0.6
    else:
        season_score = 0.3

    # Visibility proxy (from clouds + visibility distance)
    if cloud_pct < 40 and visibility > 8:
        clarity_score = 1.0
    elif visibility > 5:
        clarity_score = 0.7
    else:
        clarity_score = 0.4

    # ----------------------
    # Weighted average model
    # ----------------------

    fai = (
        wind_score * 0.20 +
        pressure_score * 0.20 +
        moon_score * 0.15 +
        time_score * 0.20 +
        season_score * 0.15 +
        clarity_score * 0.10
    )

    return round(fai, 2)
