"""Fetches live environmental data for Goa and builds a `State` object.

Current sources
---------------
• **Weather / pressure / wind** – Open‑Meteo (no API key)
• **Sun & Moon** – Astral (deterministic)
• **Tides** – simple harmonic stub (TODO: swap for INCOIS CSV)
• **SST** – climatology placeholder; if `CMEMS_USER` & `CMEMS_PASS` secrets are
  present the function currently **skips** remote download for speed.  Hook‑up
  via copernicus‑marine‑client is next.
"""
from __future__ import annotations

import os
import math
import requests
from datetime import datetime, timezone, timedelta
from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase as moon_phase

from engine import State

# --- Constants ----------------------------------------------------------
LAT, LON = 15.5, 73.8  # Goa
LOCAL_TZ = timezone(timedelta(hours=+5, minutes=30))

# -----------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------

def _fetch_weather() -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current_weather=true&hourly=pressure_msl".format(lat=LAT, lon=LON)
    )
    data = requests.get(url, timeout=10).json()
    cw = data["current_weather"]
    # Pressure trend: current minus 3h‑ago value (if available)
    try:
        idx_now = data["hourly"]["time"].index(cw["time"])
        p_now = data["hourly"]["pressure_msl"][idx_now]
        p_prev = data["hourly"]["pressure_msl"][max(idx_now - 3, 0)]
        dP_3h = p_now - p_prev
    except Exception:
        p_now, dP_3h = cw.get("surface_pressure", 1013), 0
    return {
        "temp": cw["temperature"],
        "wind_speed": cw["windspeed"],
        "wind_dir": cw["winddirection"],
        "pressure": p_now,
        "dP_3h": dP_3h,
    }


def _compute_tide_derivative(now: datetime) -> float:
    """Temporary sinusoid (~12.4 h) until INCOIS API is wired in."""
    hours = now.hour + now.minute / 60
    # Simple spring‑neap amplitude modulation (≈14‑day)
    day_of_cycle = (now.timetuple().tm_yday % 14) / 14
    amplitude = 1.5 * math.sin(day_of_cycle * math.pi)  # 0‑>1.5 m
    # 12.42 h lunar semidiurnal tide derivative
    dh_dt = amplitude * math.cos(2 * math.pi * hours / 12.42)
    return dh_dt


def _sun_moon_metrics(now: datetime) -> tuple[float, float, float]:
    loc = LocationInfo(latitude=LAT, longitude=LON)
    s = sun(loc.observer, date=now.date(), tzinfo=LOCAL_TZ)
    # PCI: how close high tide is to sunrise/sunset – here stubbed at random 0.5
    pci = 0.5
    # Minutes since nearest moon transit stub (needs true tide) → 0
    mtw = 0.0
    return pci, mtw, moon_phase(now)


def get_state_now() -> State:
    """Public helper used by Streamlit."""
    now = datetime.now(tz=LOCAL_TZ)
    w = _fetch_weather()
    pci, mtw, _ = _sun_moon_metrics(now)

    state = State(
        T=w["temp"],
        dT_dt=0.0,          # placeholder – add 3‑h temp trend later
        dh_dt=_compute_tide_derivative(now),
        pci=pci,
        mtw=mtw,
        dP_3h=w["dP_3h"],
        wspd=w["wind_speed"],
        onshore=90 < w["wind_dir"] < 270,  # rough check
        chl=0.3,             # placeholder until CMEMS download wired
        salinity_class=1,
    )
    return state
