import json
import math

# Load species intelligence once
with open("species.json", "r") as f:
    species_data = json.load(f)

def get_tactic_kit(state: dict) -> list:
    """
    Match environment to active species and return tactical playbook.
    Returns top 3 ranked species with full recommendations.
    """

    active = []

    for species in species_data:
        score = 1.0

        # ---- Seasonality boost ----
        peak = species["peak_month"]
        spread = species["month_spread"]
        month = state["month"]

        # Distance from peak, Gaussian-style decay
        delta = min(abs(month - peak), 12 - abs(month - peak))
        season_multiplier = math.exp(-0.5 * (delta / spread) ** 2)
        score *= season_multiplier

        # ---- Environmental tolerances ----
        temp_diff = abs(state["temp_c"] - species["temp_optimum_c"])
        if temp_diff > 4:
            score *= 0.4
        elif temp_diff > 2:
            score *= 0.7

        pressure_diff = abs(state["pressure_hpa"] - 1013.25)
        if pressure_diff > species["pressure_tolerance_hpa"]:
            score *= 0.6

        # ---- Clarity filter ----
        if _inferred_clarity(state) not in species["water_clarity"]:
            score *= 0.5

        # Save score
        species_copy = species.copy()
        species_copy["score"] = round(score, 3)
        active.append(species_copy)

    # Sort by score, return top 3
    top = sorted(active, key=lambda x: x["score"], reverse=True)[:3]
    return [_format_species_card(s) for s in top]

# -------------------- Inferred Logic Helpers --------------------

def _inferred_clarity(state: dict) -> str:
    """Estimate water clarity from visibility + clouds"""
    if state["cloud_pct"] < 40 and state["visibility_km"] > 8:
        return "clear"
    elif state["visibility_km"] > 5:
        return "stained"
    else:
        return "muddy"

def _format_species_card(species: dict) -> dict:
    """Format output structure for UI display"""

    return {
        "name": species["common_name"],
        "score": species["score"],
        "natural_baits": ", ".join(species["natural_baits"]),
        "lures": ", ".join(species["artificial_lures"]),
        "colour": species["lure_colour"],
        "rigs": ", ".join(species["rig_types"]),
        "retrieve_style": species["retrieve_style"],
        "water_column": species["water_column"],
        "rationale": species["notes"]
    }
