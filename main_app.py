from datetime import datetime
import streamlit as st

from data_fetcher import get_state_now
from engine import calc_fai
from tactics import get_tactic_kit

# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------

st.set_page_config(
    page_title="Goa Fish Predictor",
    page_icon="🎣",
    layout="centered",
)

st.title("🎣 Goa Fish Predictor – Live Tactical MVP")

st.markdown(
    "Physics‑first coastal fishing predictor for **Goa (15.5 °N, 73.8 °E)**.\n\n"
    "Powered by live weather + moon phase and species-specific logic – *no catch logs required.*"
)

# ----------------------------------------------------------------------
# Core logic – Fetch environment
# ----------------------------------------------------------------------

state = get_state_now()
fai = calc_fai(state)
tactics = get_tactic_kit(state)

# ----------------------------------------------------------------------
# Verdict
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
# Tactical Recommendations
# ----------------------------------------------------------------------

st.markdown("---")
st.header("🧠 Tactical Game Plan (Top 3 species)")

for species in tactics:
    st.subheader(f"🎣 {species['name']} — {species['score'] * 100:.0f}% Match")
    st.markdown(f"""
    - **Natural Baits**: {species['natural_baits']}
    - **Artificial Lures**: {species['lures']} ({species['colour']} colour)
    - **Retrieve Style**: {species['retrieve_style']}
    - **Water Column**: {species['water_column']}
    - **Recommended Rigs**: {species['rigs']}
    """)
    st.caption(f"📌 _Why this fish now:_ {species['rationale']}")

# ----------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------

st.markdown("---")
st.caption(
    "_Weather via Open‑Meteo | Moon phase integrated | SST + INCOIS tides coming soon._"
)
