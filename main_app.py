import streamlit as st
from datetime import datetime, timedelta

from data_fetcher import get_state_now
from engine import calc_fai
from tactics import get_tactic_kit

# -------------------- UI CONFIG --------------------

st.set_page_config(
    page_title="Goa Fish Predictor",
    page_icon="🎣",
    layout="centered",
    initial_sidebar_state="auto"
)

# Custom dark theme styling
st.markdown(
    """
    <style>
    body { background-color: #0D0F14; color: #E4E7EC; }
    .stApp { background-color: #0D0F14; }
    .st-bx { background-color: #1A1D24 !important; border-radius: 12px; padding: 16px; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- HEADER --------------------

st.title("🎣 Goa Fish Predictor – Live Tactical Planner")
st.caption("Physics-based predictions using live weather, tides, SST, and species biology.")

# -------------------- LOCATION SELECTOR --------------------

GOA_SPOTS = {
    "Chapora River Mouth": (15.6155, 73.7383),
    "Aguada Jetty": (15.4781, 73.8017),
    "Dona Paula": (15.4610, 73.8023),
    "Zuari Estuary": (15.3801, 73.8773),
    "Palolem": (15.0107, 74.0230)
}

spot_name = st.selectbox("📍 Choose a fishing spot", list(GOA_SPOTS.keys()))
lat, lon = GOA_SPOTS[spot_name]

# -------------------- INTERACTION MODE --------------------

mode = st.radio(
    "🎛️ Choose prediction mode:",
    ["🎣 I want to fish at a specific time", "🧠 Show me the best times to go"],
    horizontal=True
)

# -------------------- TIME INPUT --------------------

if mode == "🎣 I want to fish at a specific time":
    dt_input = st.datetime_input(
        "🕐 When do you plan to fish?",
        value=datetime.now() + timedelta(hours=1),
        step=3600
    )
    user_time = dt_input
else:
    user_time = datetime.now()  # placeholder, will scan future windows later

# -------------------- FETCH ENVIRONMENT + COMPUTE --------------------

state = get_state_now(lat=lat, lon=lon, target_time=user_time)
fai = calc_fai(state)

# -------------------- DISPLAY FAI METRIC --------------------

st.subheader("🎯 Fish Activity Index")
st.metric(label="Predicted FAI", value=f"{fai:.2f}")

if fai < 0.40:
    verdict = "🔴 **Poor** — Better spend time tying rigs or scouting."
elif fai < 0.65:
    verdict = "🟠 **Fair** — Try dawn/dusk with stealth."
elif fai < 0.80:
    verdict = "🟡 **Good** — Decent chance of hookups."
else:
    verdict = "🟢 **Great** — Conditions are firing!"

st.markdown(verdict)

# -------------------- TACTIC GAMEPLAN --------------------

st.subheader("🧠 Tactical Game Plan")

gameplan = get_tactic_kit(state)

for species in gameplan:
    with st.expander(f"🎯 {species['name']}"):
        st.markdown(f"""
        - **Target Zone**: {species['water_column']}
        - **Best Bait**: {species['natural_baits']}
        - **Recommended Lures**: {species['lures']}
        - **Rig Type**: {species['rigs']}
        - **Retrieve Style**: {species['retrieve_style']}
        - **Lure Colour**: {species['colour']}
        - **Why**: {species['rationale']}
        """)

# -------------------- FOOTER --------------------

st.caption("📡 Live data: OpenWeatherMap · INCOIS (tide model) · Copernicus SST\n🧠 All predictions are biologically driven, not AI hallucinated.")
