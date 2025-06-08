from datetime import datetime, timedelta
import streamlit as st

from data_fetcher import get_state
from engine import calc_fai
from tactics import get_tactic_kit

# ----------------------------------------------------------------------
# Page Setup
# ----------------------------------------------------------------------

st.set_page_config(
    page_title="Goa Fish Predictor",
    page_icon="🎣",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🎣 Goa Fish Predictor – Tactical AI")

st.markdown(
    "Physics‑first coastal fishing predictor for **Goa (15.5 °N, 73.8 °E)**\n\n"
    "*Uses live environmental data, lunar logic, and seasonal fish behavior — no catch logs needed.*"
)

# ----------------------------------------------------------------------
# Time Input – User can ask for future prediction
# ----------------------------------------------------------------------

with st.expander("🎯 When are you planning to fish?"):
    user_time = st.slider(
        "Pick your target fishing time (forecast range: now to 72 hours ahead)",
        min_value=datetime.now(),
        max_value=datetime.now() + timedelta(days=3),
        value=datetime.now() + timedelta(hours=1),
        format="DD MMM HH:mm"
    )

# ----------------------------------------------------------------------
# Get Environment for the Requested Time
# ----------------------------------------------------------------------

state = get_state(user_time)
fai = calc_fai(state)
tactics = get_tactic_kit(state)

# ----------------------------------------------------------------------
# Display FAI + Verdict
# ----------------------------------------------------------------------

st.subheader(f"🌐 Environmental Snapshot for {user_time.strftime('%a, %d %b %I:%M %p')}")
st.metric("🧪 Fish Activity Index", f"{fai:.2f}")

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
# Tactical Game Plan
# ----------------------------------------------------------------------

st.markdown("---")
st.header("🎣 Tactical Game Plan – Top 3 Species to Target")

for species in tactics:
    st.subheader(f"{species['name']} — {species['score'] * 100:.0f}% Match")
    st.markdown(f"""
    - **Natural Baits**: {species['natural_baits']}
    - **Artificial Lures**: {species['lures']} (**{species['colour']}** colour)
    - **Retrieve Style**: {species['retrieve_style']}
    - **Water Column**: {species['water_column']}
    - **Recommended Rigs**: {species['rigs']}
    """)
    st.caption(f"🧠 _Why this species now:_ {species['rationale']}")

# ----------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------

st.markdown("---")
st.caption(
    "_Weather via Open‑Meteo | Lunar phase calculated | SST (CMEMS) and real INCOIS tides coming soon._"
)
