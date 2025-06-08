"""Streamlit front‑end for the Goa Fish Predictor (live data version).
Paste this file in the repo root, replacing the old placeholder demo.
"""
from datetime import datetime
import streamlit as st

from data_fetcher import get_state_now
from engine import calc_fai

# ----------------------------------------------------------------------
# Page layout & header
# ----------------------------------------------------------------------

st.set_page_config(
    page_title="Goa Fish Predictor",
    page_icon="🐟",
    layout="centered",
)

st.title("🎣 Goa Fish Predictor – Live MVP")

st.markdown(
    "Physics‑first coastal fishing predictor for *15.5 °N, 73.8 °E* (Goa).\n"
    "Uses live weather, synthetic tide curve, and deterministic maths – **no catch logs required**."
)

# ----------------------------------------------------------------------
# Core logic – fetch live state & compute index
# ----------------------------------------------------------------------

state = get_state_now()              # live environmental snapshot
fai   = calc_fai(state)              # 0 – 1 scale

# ----------------------------------------------------------------------
# Display section
# ----------------------------------------------------------------------

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
    "_Live weather sourced from Open‑Meteo; tide derivative is a synthetic harmonic placeholder.\n"
    "Full INCOIS tide curves and CMEMS SST integration coming next._"
)
