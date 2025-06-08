"""data_fetcher.py – Live environmental snapshot builder for Goa Fish Predictor.

Sources (MVP)
-------------
• Weather / pressure / wind  → Open-Meteo  (no API key)
• Sun / moon metrics         → Astral      (deterministic)
• Tide derivative            → Synthetic 12.42 h sinusoid (placeholder)
• SST / chlorophyll          → Placeholder constant (hook CMEMS later)

Main public helper
------------------
get_state_now(lat: float = 15.488, lon: float = 73.827) -> engine.State
"""

from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta
import requests
from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase as moon_phase

from engine import State  # <-- our physics-first FAI engine

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
LOCAL_TZ = timezone(timedelta(hours=5, minutes=30))  # IST (Goa)

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def _fetch_weather(lat: float, lon: float) -> dict:
    """Return dict with temperature, 3-h temp trend, wind, and 3-h pressure trend."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&hourly=pressure_msl,temperature_2m"
    )
    data = requests.get(url, timeout=10).json()
    cw = data["current_weather"]

    # Locate index of current time in hourly arrays
    idx_now = data["hourly"]["time"].index(cw["time"])

    # Temperature and 3-h trend
    t_now  = data["hourly"]["temperature_2m"][idx_now]
    t_prev = data["hourly"]["temperature_2m"][max(idx_now - 3, 0)]
    dT_3h  = t_now - t_prev

    # Pressure and 3-h trend
    p_now  = data["hourly"]["pressure_msl"][idx_now]
    p_prev = data["hourly"]["pressure_msl"][max(idx_now - 3, 0)]
    dP_3h  = p_now - p_prev

    return {
        "temp": t_now,
        "dT_3h": dT_3h,
        "wind_speed": cw["windspeed"],
        "wind_dir": cw["winddirection"],
        "dP_3h": dP_3h,
    }


def _compute_tide_derivative(now: datetime) -> float:
    """Synthetic 12.42 h sinusoid with spring-neap modulation (placeholder)."""
    hours = now.hour + now.minute / 60
    day_of_cycle = (now.timetuple().tm_yday % 14) / 14       # 0-1
    amplitude = 1.5 * math.sin(day_of_cycle * math.pi)        # ~0–1.5 m
    dh_dt = amplitude * math.cos(2 * math.pi * hours / 12.42) # m h-1
    return dh_dt


def _sun_moon_metrics(now: datetime, lat: float, lon: float) -> tuple[float, float]:
    """Return PCI (placeholder 0.5) and minutes-to-moon-transit (placeholder 0)."""
    # Full implementation will need real high-tide timing.
    pci = 0.5   # Phase-Concordance Index stub
    mtw = 0.0   # Minutes to nearest moon transit stub
    return pci, mtw


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
def get_state_now(lat: float = 15.488, lon: float = 73.827) -> State:
    """Build an engine.State for the given coordinates (default: Miramar beach)."""
    now = datetime.now(tz=LOCAL_TZ)

    weather = _fetch_weather(lat, lon)
    pci, mtw = _sun_moon_metrics(now, lat, lon)

    state = State(
        T=weather["temp"],
        dT_dt=weather["dT_3h"],
        dh_dt=_compute_tide_derivative(now),
        pci=pci,
        mtw=mtw,
        dP_3h=weather["dP_3h"],
        wspd=weather["wind_speed"],
        onshore=90 < weather["wind_dir"] < 270,  # simple on-shore check
        chl=0.3,               # placeholder until CMEMS wired in
        salinity_class=1,      # 1 = oceanic
    )
    return state
