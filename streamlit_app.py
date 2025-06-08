import streamlit as st
from datetime import datetime, timedelta
import pytz

from data_fetcher import get_state_now
from engine import evaluate_targets

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Goa Fish Predictor", page_icon="🐟", layout="centered")
st.title("🎣 Goa Fish Predictor")
st.caption("Physics-first fishing predictions for Goa using live SST, tide, weather, and species logic.")

# ──────────────────────────────────────────────────────────────
# UI MODE SELECTION
# ──────────────────────────────────────────────────────────────
mode = st.radio(
    "Choose what you want help with:",
    ["🎯 I want to go fishing at a specific time", "📈 Show me the best time to fish today"]
)

local_tz = pytz.timezone("Asia/Kolkata")
now = datetime.now(local_tz)
selected_time = now

if mode == "🎯 I want to go fishing at a specific time":
    selected_time = st.slider("🕰️ When do you plan to fish?", min_value=now, max_value=now + timedelta(days=1), value=now, step=timedelta(minutes=30))

# ──────────────────────────────────────────────────────────────
# GET LIVE DATA
# ──────────────────────────────────────────────────────────────
with st.spinner("Fetching environmental data..."):
    state = get_state_now()
    recommendations = evaluate_targets(state)

# ──────────────────────────────────────────────────────────────
# DISPLAY DATA
# ──────────────────────────────────────────────────────────────
st.subheader("📊 Environmental Snapshot")
col1, col2 = st.columns(2)
with col1:
    st.metric("🌡️ SST (°C)", f"{state['sst_c']:.1f}")
    st.metric("🌊 Tide (m)", f"{state['tide_m']:.2f}")
    st.metric("🌙 Moon", state['moon_phase'].capitalize())
with col2:
    st.metric("🌤️ Temp (°C)", f"{state['temp_c']:.1f}")
    st.metric("🌬️ Wind (kph)", f"{state['wind_kph']:.1f}")
    st.metric("📈 Pressure (hPa)", f"{state['pressure_hPa']}")

# ──────────────────────────────────────────────────────────────
# OUTPUT RECOMMENDATION
# ──────────────────────────────────────────────────────────────
st.subheader("🎣 Recommended Plan")

if mode == "📈 Show me the best time to fish today":
    best_times = recommendations.get("best_times", [])
    if best_times:
        for entry in best_times:
            st.markdown(f"🕓 **{entry['time']}** – Target **{entry['species']}** near **{entry['habitat']}** using `{entry['tactic']}`")
    else:
        st.warning("No ideal windows found today. Try dawn or dusk with natural bait near structure.")

else:
    plan = recommendations.get("plan_for_now", {})
    if plan:
        st.markdown(f"🎯 **Species:** {plan['species']}")
        st.markdown(f"📍 **Habitat:** {plan['habitat']}")
        st.markdown(f"🎒 **Tactic:** `{plan['tactic']}`")
        st.markdown(f"🎨 **Lure Colour:** {plan['color']} | **Water Column:** {plan['depth']}")
    else:
        st.warning("Fishing activity is currently low. You may still try dawn/dusk near structure with live bait.")
