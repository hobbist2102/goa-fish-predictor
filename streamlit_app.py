"""Streamlit front-end for the Goa Fish Predictor (location-aware live data).

• Lets the user pick a fishing spot in Goa.
• Fetches live weather for that lat/lon via data_fetcher.get_state_now().
• Computes Fish Activity Index (FAI) with engine.calc_fai().
"""

from __future__ import annotations

import streamlit as st
from data_fetcher import get_state_now
from engine import calc_fai

# ---------------------------------------------------------------------
# Pre-defined fishing spots (expand this dict anytime)
# ---------------------------------------------------------------------
SPOTS = {
    "Central Goa – Miramar":       (15.488, 73.827),
    "Zuari Estuary – Cortalim":    (15.385, 73.892),
    "Chapora River Mouth":         (15.610, 73.737),
    "Cabo de Rama":                (15.149, 73.924),
    "Colva Beach":                 (15.271, 73.922),
}

# ---------------------------------------------------------------------
# Page config & header
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Goa Fish Predictor",
    page_icon="🐟",
    layout="centered",
)

st.title("🎣 Goa Fish Predictor – Live MVP")

st.markdown(
    "Select a spot, fetch **live weather**, and get the Fish Activity Index. "
    "No historical catch logs needed."
)

# ---------------------------------------------------------------------
# Spot selector
# ---------------------------------------------------------------------
spot_name = st.selectbox("Choose your fishing area:", list(SPOTS.keys()))
lat, lon  = SPOTS[spot_name]
st.caption(f"Coordinates: {lat:.3f} °, {lon:.3f} ° (WGS-84)")

# ---------------------------------------------------------------------
# Core logic – live data → FAI
# ---------------------------------------------------------------------
state = get_state_now(lat, lon)
fai   = calc_fai(state)          # value between 0 and 1

# ---------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------
st.metric("Fish Activity Index", f"{fai:.2f}")

if fai < 0.40:
    verdict = "🔴 **Poor** — Better spend the time tying new rigs."
elif fai < 0.65:
    verdict = "🟠 **Fair** — Try dawn or dusk only."
elif fai < 0.80:
    verdict = "🟡 **Good** — Decent chance of action!"
else:
    verdict = "🟢 **Great** — Grab your gear and go!"

st.markdown(verdict)

st.caption(
    "_Live weather via Open-Meteo · Tide derivative is synthetic until INCOIS is wired in. "
    "CMEMS SST coming next._"
)
