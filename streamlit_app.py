import streamlit as st
import json
import datetime

from data_fetcher import get_state_now
from engine import predict_best_catch

# ----------------------------------------------------------------------
# Load Goa fishing locations
# ----------------------------------------------------------------------

with open("locations.json", "r") as f:
    LOCATION_MAP = json.load(f)

location_names = list(LOCATION_MAP.keys())

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------

st.set_page_config(
    page_title="Goa Fish Predictor",
    page_icon="🐟",
    layout="centered"
)
st.title("🎣 Goa Fish Predictor – Live MVP")

st.markdown(
    "**Physics-first coastal fishing predictor** for the Goa coastline.\n\n"
    "Uses **real-time data** from OpenWeatherMap, CMEMS SST, and INCOIS tides — "
    "_no catch logs required_."
)

# ----------------------------------------------------------------------
# Location Picker
# ----------------------------------------------------------------------

selected_location = st.selectbox("📍 Select your fishing spot:", location_names)
lat, lon = LOCATION_MAP[selected_location]
st.caption(f"Coordinates: `{lat:.4f}°, {lon:.4f}°`")

# ----------------------------------------------------------------------
# Environmental Snapshot
# ----------------------------------------------------------------------

with st.spinner("🔍 Fetching real-time data..."):
    state = get_state_now(lat, lon)
    species, score, setup, sst_value = predict_best_catch(state)

# ----------------------------------------------------------------------
# Results Display
# ----------------------------------------------------------------------

if not species:
    st.error("No prediction available. Please check your API keys or try again later.")
else:
    st.metric("🌡 Sea Surface Temp (°C)", f"{sst_value:.2f}")
    st.metric("🌊 Tide Height (m)", f"{state.get('tide_height', '?')}")

    st.subheader("🎯 Fish Activity Index (FAI)")
    if score >= 0.8:
        st.success(f"**Excellent ({score:.2f})** — High activity expected!")
    elif score >= 0.65:
        st.info(f"**Good ({score:.2f})** — Promising conditions.")
    elif score >= 0.5:
        st.warning(f"**Fair ({score:.2f})** — Try peak hours.")
    else:
        st.error(f"**Poor ({score:.2f})** — Not the best time.")

    st.subheader("🎣 Predicted Catch & Strategy")
    st.markdown(f"**🎯 Target Species**: `{species}`")
    st.markdown(f"**🧰 Recommended Setup**: `{setup}`")

# ----------------------------------------------------------------------
# Data Sources Footer
# ----------------------------------------------------------------------

st.caption(
    "_Live data from OpenWeatherMap, CMEMS (SST), and WorldTides (Mormugao tide station)._\n"
    "_Built with love by coastal fishing nerds 🐠_"
)
