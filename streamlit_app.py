import streamlit as st
from datetime import datetime
import random
from engine import State, calc_fai

st.set_page_config(page_title="Goa Fish Predictor", page_icon="🐟", layout="centered")
st.title("🎣 Goa Fish Predictor – MVP")

st.markdown(
    "This **physics‑first** prototype rates feeding windows \n"
    "for inshore game fish near *15.5 °N, 73.8 °E* with **no catch logs**.")

from data_fetcher import get_state_now
...
state = get_state_now()   # ← live data instead of random numbers

st.metric("Fish Activity Index", f"{fai:.2f}")

if fai < 0.4:
    verdict = "🔴 **Poor** — Better spend the time tying new rigs."
elif fai < 0.65:
    verdict = "🟠 **Fair** — Try dawn or dusk only."
elif fai < 0.80:
    verdict = "🟡 **Good** — Decent chance of action!"
else:
    verdict = "🟢 **Great** — Grab your gear and go!"

st.markdown(verdict)

st.caption("_Note: this demo uses randomised inputs. Real APIs will be wired in next._")
