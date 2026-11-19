"""Alternative attacker footprints for the footprint-swap test (E3).

All variants first leave the signal the way a tap does (``sqrt(1 - tau)`` amplitude) and then add one kind of
residual, after which the power is restored to the nominal level (power-compensated attacker, as the alpha ladder is
from alpha = 0.5 on). Each has one scale parameter that is calibrated so the variants are equally detectable by a
supervised feature-space oracle (see ``experiments.match_footprints``).

  ladder        the original alpha ladder (``attacker.make_attack``)
  noise_only    white insertion noise, relative variance ``scale`` (echo off)
  echo_only     one-symbol echo of relative amplitude ``scale`` (noise off)
  colored_noise AR(1) insertion noise (rho 0.9), relative variance ``scale``
  phase_jitter  i.i.d. symbol phase jitter, standard deviation ``scale`` radians
"""

from __future__ import annotations

import numpy as np
from scipy.signal import lfilter

from ..attacker import make_attack
from ..channel import cgauss

KINDS = ("ladder", "noise_only", "echo_only", "colored_noise", "phase_jitter")
SCALE_RANGE = {"noise_only": (1e-5, 3e-1), "echo_only": (1e-3, 0.6),
               "colored_noise": (1e-5, 3e-1), "phase_jitter": (1e-3, 0.8)}
COLOR_RHO = 0.9


def build_attack(spec: dict, cfg_attacker: dict, nominal_power: float, start_symbol: int = 0):
    """Return ``attack(x, rng)`` for a footprint spec such as ``{"kind": "echo_only", "scale": 0.05}``
    or ``{"kind": "ladder", "alpha": 0.5}``."""
    kind = spec["kind"]
    if kind == "ladder":
        return make_attack(cfg_attacker, float(spec["alpha"]), nominal_power, start_symbol)
    if kind not in SCALE_RANGE:
        raise ValueError(f"unknown footprint kind {kind!r}")
    tau = float(cfg_attacker["tap_fraction"])
    s = float(spec["scale"])

    def attack(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        y = x.copy()
        u = np.sqrt(1.0 - tau) * x[start_symbol:]
        if kind == "echo_only":
            u = (u + s * np.roll(u, 1)) / np.sqrt(1.0 + s * s)
        elif kind == "noise_only":
            u = u + cgauss(rng, u.shape, s * (1.0 - tau) * nominal_power)
        elif kind == "colored_noise":
            w = cgauss(rng, u.shape, 1.0)
            n = lfilter([np.sqrt(1.0 - COLOR_RHO ** 2)], [1.0, -COLOR_RHO], w)
            u = u + n * np.sqrt(s * (1.0 - tau) * nominal_power)
        elif kind == "phase_jitter":
            u = u * np.exp(1j * rng.normal(0.0, s, u.shape))
        p_now = float(np.mean(np.abs(u) ** 2))
        y[start_symbol:] = u * np.sqrt(nominal_power / p_now)  # restore nominal power
        return y

    return attack
