"""Streamlit front‑end for the Goa Fish Predictor (location‑aware).

Choose a fishing area within Goa; the app fetches live environmental data for
that lat/lon and computes the Fish Activity Index.
"""
from __future__ import annotations

import streamlit as st

from data_fetcher import get_state_now
from engine import calc_fai

# ---------------------------------------------------------------------
# Pre‑defined fishing spots (expand anytime)
# ---------------------------------------------------------------------

SPOTS = {
    "Central Goa (Miramar)": (15.488, 73.827),
    "Zuari Estuary (Cortalim)": (15.385, 73.892),
    "Chapora Mouth": (15.610, 73.737),
    "Cabo de Rama": (15.149, 73.924),
    "Colva Beach": (15.271, 73.922),
}

# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Goa Fish Predictor",
    page_icon="🐟",
    layout="centered",
)

st.title("🎣 Goa Fish Predictor – Live MVP")
st.markdown("Select a spot, get an instant activity score. No catch logs needed.")

# ---------------------------------------------------------------------
# Spot selector
# ---------------------------------------------------------------------

spot_name = st.selectbox("Choose your fishing area:", list(SPOTS.keys()))
lat, lon = SPOTS[spot_name]

st.caption(f"Coordinates: {lat:.3f}°, {lon:.3f}° (WGS84)")

# ---------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------

state = get_state_now(lat, lon)
fai = calc_fai(state)

# ---------------------------------------------------------------------
# Display results
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

st.caption("Live weather from Open‑Meteo; tide derivative is synthetic until INCOIS is wired in. Spot list is editable in `SPOTS` dict.")
