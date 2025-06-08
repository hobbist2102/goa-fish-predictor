import streamlit as st
from datetime import datetime
import random
from engine import State, calc_fai

st.set_page_config(page_title="Goa Fish Predictor", page_icon="🐟", layout="centered")
st.title("🎣 Goa Fish Predictor – MVP")

st.markdown(
    "This **physics‑first** prototype rates feeding windows \n"
    "for inshore game fish near *15.5 °N, 73.8 °E* with **no catch logs**.")

# -- Placeholder inputs -------------------------------------------------

now = datetime.utcnow()

# In a real app these will come from APIs; for demo we randomise
state = State(
    T= random.uniform(27.0, 29.8),
    dT_dt= random.uniform(-0.3, 0.3),
    dh_dt= random.uniform(-1.5, 1.5),
    pci= random.uniform(0, 1),
    mtw= random.uniform(-180, 180),
    dP_3h= random.uniform(-3, 3),
    wspd= random.uniform(0, 10),
    onshore= random.choice([True, False]),
    chl= random.uniform(0.1, 1.0),
    salinity_class=1,
)

fai = calc_fai(state)

# -- Display ------------------------------------------------------------

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
