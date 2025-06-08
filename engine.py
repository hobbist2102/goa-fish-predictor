import json
from datetime import datetime, timedelta

with open("species.json", "r") as f:
    SPECIES_DB = json.load(f)["species"]

def _score_species(species, env):
    score = 0

    # Temperature
    opt = species["temperature_preference"]["optimal"]
    min_t, max_t = species["temperature_preference"]["tolerance"]
    if min_t <= env["sst_c"] <= max_t:
        score += 1 - abs(env["sst_c"] - opt) / (max_t - min_t)

    # Pressure
    score += 1 if abs(env["pressure_hPa"] - 1013) <= species.get("pressure_tolerance_hPa", 5) else 0

    # Moon phase
    if species["feeding_triggers"].get("moon_phase") in ["full", "new", env["moon_phase"]]:
        score += 0.5

    # Water turbidity (est. via cloud + wind)
    if env["cloud_pct"] > 60 or env["wind_kph"] > 18:
        water_type = "muddy"
    elif env["cloud_pct"] > 30:
        water_type = "stained"
    else:
        water_type = "clear"
    if water_type in species.get("lure_color", {}):
        score += 0.5

    # Month/Season
    now_month = env["datetime"].month
    peak = species["monthly_seasonality"]["peak_month"]
    spread = species["monthly_seasonality"]["spread_months"]
    month_diff = min(abs(now_month - peak), 12 - abs(now_month - peak))
    if month_diff <= spread // 2:
        score += 1

    return score

def _generate_tactic(species, water_type):
    bait = species["bait"]["natural"][0] if species["bait"]["natural"] else "live bait"
    color = species["lure_color"].get(water_type, "natural")
    tactic = species["retrieve_style"][0] if species["retrieve_style"] else "steady retrieve"
    depth = species["water_column"]
    rig = species["rig_types"][0] if species["rig_types"] else "standard rig"

    return {
        "species": species["common_name"],
        "habitat": ", ".join(species["preferred_habitat"]),
        "tactic": f"{bait} / {tactic} / {rig}",
        "color": color,
        "depth": depth
    }

def evaluate_targets(env):
    output = {"plan_for_now": None, "best_times": []}

    # Water type
    if env["cloud_pct"] > 60 or env["wind_kph"] > 18:
        water_type = "muddy"
    elif env["cloud_pct"] > 30:
        water_type = "stained"
    else:
        water_type = "clear"

    # Score all species
    scored = []
    for sp in SPECIES_DB:
        sp_score = _score_species(sp, env)
        if sp_score >= 2:  # basic cutoff
            scored.append((sp_score, sp))

    scored.sort(reverse=True, key=lambda x: x[0])

    # Plan for now
    if scored:
        best = scored[0][1]
        output["plan_for_now"] = _generate_tactic(best, water_type)

    # Best times in next 24hr (simulate)
    now = env["datetime"]
    for hour_offset in range(0, 24, 2):
        fake_env = env.copy()
        fake_env["datetime"] = now + timedelta(hours=hour_offset)
        best_score = 0
        best_species = None
        for sp in SPECIES_DB:
            score = _score_species(sp, fake_env)
            if score > best_score:
                best_score = score
                best_species = sp
        if best_species:
            output["best_times"].append({
                "time": fake_env["datetime"].strftime("%I:%M %p"),
                "species": best_species["common_name"],
                "habitat": best_species["preferred_habitat"][0],
                "tactic": best_species["retrieve_style"][0] if best_species["retrieve_style"] else "trolling"
            })

    return output
