import streamlit as st
import json
from datetime import datetime

from data_fetcher import get_state_now
from engine import calc_fai, recommend_plan

# ----------------------------------------------------------------------
# Load Goa fishing locations
# ----------------------------------------------------------------------

with open("locations.json", "r") as f:
    LOCATION_MAP = json.load(f)

location_names = list(LOCATION_MAP.keys())

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------

st.set_page_config(page_title="Goa Fish Predictor", page_icon="🐟", layout="centered")
st.title("🎣 Goa Fish Predictor – Goa-wide Live MVP")

st.markdown(
    "**Physics-first coastal fishing predictor** for the Goa coastline.\n\n"
    "Uses **real-time data** from OpenWeatherMap, CMEMS SST, and INCOIS tides — "
    "**no catch logs required**.\n"
)

# ----------------------------------------------------------------------
# Location Picker
# ----------------------------------------------------------------------

selected_location = st.selectbox("📍 Select your fishing spot:", location_names)
lat, lon = LOCATION_MAP[selected_location]
st.caption(f"Coordinates: `{lat:.4f}°, {lon:.4f}°`")

# ----------------------------------------------------------------------
# Live Environmental Snapshot
# ----------------------------------------------------------------------

state = get_state_now(lat, lon)
fai = calc_fai(state)

# ----------------------------------------------------------------------
# Display FAI
# ----------------------------------------------------------------------

st.metric("🎯 Fish Activity Index", f"{fai:.2f}")

if fai < 0.40:
    verdict = "🔴 **Poor** — Better spend the time tying new rigs."
elif fai < 0.65:
    verdict = "🟠 **Fair** — Try dawn or dusk only."
elif fai < 0.80:
    verdict = "🟡 **Good** — Decent chance of action!"
else:
    verdict = "🟢 **Great** — Grab your gear and go!"

st.markdown(verdict)

# ----------------------------------------------------------------------
# Game Plan Recommendations
# ----------------------------------------------------------------------

plan = recommend_plan(state, lat, lon)
st.subheader("🎣 Tactical Game Plan")
st.markdown(plan)

# ----------------------------------------------------------------------
# Data Footer
# ----------------------------------------------------------------------

st.caption(
    "_Live weather: Open‑Meteo | Tides: INCOIS | SST: CMEMS (auth required)_"
)
