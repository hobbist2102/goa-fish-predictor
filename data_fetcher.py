"""data_fetcher.py – Live environmental snapshot builder for Goa Fish Predictor.

This is the **correct** version. The file should NOT import itself. If your
GitHub `data_fetcher.py` currently starts with `from data_fetcher import ...`,
replace its entire contents with this block.

Sources (MVP)
-------------
• Weather / pressure / wind  → Open-Meteo  (no API key)
• Sun / moon metrics         → Astral      (deterministic)
• Tide derivative            → Synthetic 12.42 h sinusoid (placeholder)
• SST / chlorophyll          → Constant placeholder (hook CMEMS later)

Public helper
-------------
get_state_now(lat: float = 15.488, lon: float = 73.827) → engine.State
"""
from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import requests
from astral import LocationInfo
from astral.sun import sun

from engine import State

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
LOCAL_TZ = ZoneInfo("Asia/Kolkata")  # IST (UTC+5:30)

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def _fetch_weather(lat: float, lon: float) -> dict:
    """Return dict with temperature, 3‑h temp trend, wind, and 3‑h pressure trend."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true&timezone=UTC"
        "&hourly=temperature_2m,pressure_msl"
    )
    data = requests.get(url, timeout=10).json()
    cw = data["current_weather"]

    # Find nearest hourly index; fallback to last record if exact time missing
    try:
        idx_now = data["hourly"]["time"].index(cw["time"])
    except ValueError:
        idx_now = -1

    t_now  = data["hourly"]["temperature_2m"][idx_now]
    t_prev = data["hourly"]["temperature_2m"][max(idx_now - 3, 0)]
    dT_3h  = t_now - t_prev

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
    """Synthetic tide derivative – replace with INCOIS when ready."""
    hours = now.hour + now.minute / 60
    day_fraction = (now.timetuple().tm_yday % 14) / 14  # spring–neap cycle
    amplitude = 1.5 * math.sin(day_fraction * math.pi)  # ~0–1.5 m
    dh_dt = amplitude * math.cos(2 * math.pi * hours / 12.42)
    return dh_dt


def _sun_moon_metrics(lat: float, lon: float) -> tuple[float, float]:
    """Return phase‑concordance index & moon‑transit delta (placeholders)."""
    pci = 0.5  # neutral until real high‑tide data available
    mtw = 0.0
    return pci, mtw

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def get_state_now(lat: float = 15.488, lon: float = 73.827) -> State:
    """Return an engine.State populated with **live** weather for given coords."""
    now = datetime.now(tz=LOCAL_TZ)

    w = _fetch_weather(lat, lon)
    pci, mtw = _sun_moon_metrics(lat, lon)

    return State(
        T=w["temp"],
        dT_dt=w["dT_3h"],
        dh_dt=_compute_tide_derivative(now),
        pci=pci,
        mtw=mtw,
        dP_3h=w["dP_3h"],
        wspd=w["wind_speed"],
        onshore=90 < w["wind_dir"] < 270,
        chl=0.3,          # placeholder until CMEMS wired
        salinity_class=1,
    )
