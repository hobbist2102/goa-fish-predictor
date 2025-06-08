import json
import math
from pathlib import Path

# ----------------------------------------------------
# Load species intelligence
# ----------------------------------------------------

with open(Path(__file__).parent / "species.json", "r", encoding="utf-8") as f:
    species_db = json.load(f)["species"]

# ----------------------------------------------------
# Compute Fish Activity Index (simple 0-1 scale)
# ----------------------------------------------------

def calc_fai(state):
    """
    High-level heuristic index for fishing conditions (0 = bad, 1 = excellent).
    Factors: temp, pressure, cloud, tide, moon phase, SST
    """
    temp = state["temp_c"]
    pressure = state["pressure_hpa"]
    cloud = state["cloud_pct"]
    tide = state["tide_m"]
    moon = state["moon_phase"]

    score = 0

    # Ideal temperature range boost
    score += 0.25 if 24 <= temp <= 29 else 0.10

    # Moderate cloud cover is good
    score += 0.15 if 20 <= cloud <= 60 else 0.05

    # Tide not too low or too high
    score += 0.20 if 0.6 <= tide <= 2.2 else 0.05

    # Moon phase (full/new) bonus
    if moon < 10 or moon > 90:
        score += 0.15
    else:
        score += 0.05

    # Pressure tolerance (minimal change assumed OK)
    score += 0.15

    return min(round(score, 2), 1.0)

# ----------------------------------------------------
# Tactical Engine: Scores each species and returns top 3
# ----------------------------------------------------

def get_tactic_kit(state):
    temp = state["temp_c"]
    pressure = state["pressure_hpa"]
    moon = state["moon_phase"]
    tide = state["tide_m"]
    month = state["month"]

    scored_species = []

    for fish in species_db:
        s = 0
        notes = []

        # Temperature range match
        if fish["temperature_preference"]["tolerance"][0] <= temp <= fish["temperature_preference"]["tolerance"][1]:
            s += 0.25
            notes.append("✅ Optimal temperature match")
        else:
            notes.append("⚠️ Temperature outside best range")

        # Month = peak or nearby
        peak = fish["monthly_seasonality"]["peak_month"]
        spread = fish["monthly_seasonality"]["spread_months"]
        delta = min(abs(month - peak), 12 - abs(month - peak))
        if delta <= spread // 2:
            s += 0.20
            notes.append("✅ In seasonal window")
        else:
            notes.append("❌ Off-season")

        # Pressure assumed stable
        s += 0.15
        notes.append("✅ Stable barometric pressure")

        # Moon phase (only if specified)
        if "moon_phase" in fish.get("feeding_triggers", {}):
            if moon < 10 or moon > 90:
                s += 0.10
                notes.append("🌑 Favorable moon phase")
            else:
                notes.append("🌕 Moon phase neutral")

        # Tide match (general logic)
        if 0.5 < tide < 2.5:
            s += 0.10
            notes.append("🌊 Acceptable tide height")
        else:
            notes.append("⚠️ Unusual tide height")

        # Water column bonus
        if "water_column" in fish:
            s += 0.10

        scored_species.append({
            "name": fish["common_name"],
            "score": round(s, 2),
            "natural_baits": ", ".join(fish["bait"]["natural"]),
            "lures": ", ".join(fish["bait"]["artificial"]),
            "colour": fish["lure_color"]["clear"],  # can match to current water later
            "retrieve_style": ", ".join(fish["retrieve_style"]),
            "rigs": ", ".join(fish["rig_types"]),
            "water_column": fish["water_column"],
            "rationale": " | ".join(notes)
        })

    top_3 = sorted(scored_species, key=lambda x: x["score"], reverse=True)[:3]
    return top_3
