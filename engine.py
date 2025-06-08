"""Physics‑first Fish Activity Index (FAI) engine for Goa inshore species.
Works with **zero** historical catch logs.
"""
from __future__ import annotations
import math

# ---------------------------------------------------------------------
# Helper curves
# ---------------------------------------------------------------------

def gaussian(x: float, mu: float, sigma: float) -> float:
    """Unit‑height Gaussian curve."""
    return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

def tide_score(dh_dt: float, k: float = 1.3) -> float:
    """Score moving water; positive `dh_dt` = flooding tide."""
    return (1.0 + math.tanh(k * dh_dt)) / 2.0

# ---------------------------------------------------------------------
# Core FAI calculation
# ---------------------------------------------------------------------

DEFAULT_WEIGHTS = {
    "Topt": 0.20,
    "Ttrend": 0.05,
    "Tide": 0.20,
    "PCI": 0.075,
    "MTW": 0.075,
    "Pressure": 0.10,
    "Wind": 0.10,
    "Chl": 0.10,
    "Fresh": 0.10,
}

class State:
    """Container holding all environmental variables for one time‑step."""
    def __init__(
        self,
        T: float,
        dT_dt: float,
        dh_dt: float,
        pci: float,
        mtw: float,
        dP_3h: float,
        wspd: float,
        onshore: bool,
        chl: float,
        salinity_class: int,  # 1 = oceanic, 0 = brackish
    ) -> None:
        self.T = T
        self.dT_dt = dT_dt
        self.dh_dt = dh_dt
        self.pci = pci
        self.mtw = mtw
        self.dP_3h = dP_3h
        self.wspd = wspd
        self.onshore = onshore
        self.chl = chl
        self.salinity_class = salinity_class


def calc_fai(state: State, weights: dict[str, float] | None = None) -> float:
    """Return Fish Activity Index in [0, 1]."""
    w = weights or DEFAULT_WEIGHTS
    eps = 1e-6  # avoid log(0)

    scores = {
        "Topt": gaussian(state.T, 29.0, 1.5),
        "Ttrend": 1 / (1 + math.exp(state.dT_dt)),  # cooling penalised
        "Tide": tide_score(state.dh_dt),
        "PCI": state.pci,   # already scaled 0‑1 before injection
        "MTW": gaussian(state.mtw, 0, 90),
        "Pressure": 1 / (1 + math.exp(abs(state.dP_3h) - 2)),
        "Wind": gaussian(state.wspd, 4, 3) * (1 if state.onshore else 0.6),
        "Chl": min(state.chl / 0.5, 1.0),
        "Fresh": 1 - 0.5 * (1 - state.salinity_class),
    }

    log_sum = sum(w[key] * math.log(scores[key] + eps) for key in w)
    return math.exp(log_sum)
