"""M2: eavesdropper models acting on the fiber output, before the handover.

The tap leaves a footprint with three parts, one per statistical order:
  1. mean     - power drop: the tap removes a fraction ``tap_fraction`` of the power;
  2. variance - excess noise from the insertion hardware, at SNR ``excess_snr_db``
                relative to the tapped signal;
  3. higher   - a one-symbol echo of relative amplitude ``echo`` (insertion
                reflection), which reshapes the amplitude distribution (ISI).
Footprint sizes are modelling assumptions (see experiments/configs/base.yaml).

Fidelity ``alpha`` in [0, 1] is how much of the footprint the attacker hides,
order by order, piecewise linear:
  r_mean = min(alpha / 0.5, 1)              mean restored over 0    -> 0.5
  r_var  = clip((alpha - 0.5) / 0.25, 0, 1) variance matched over 0.5  -> 0.75
  r_high = clip((alpha - 0.75) / 0.25, 0, 1) higher order matched over 0.75 -> 1
alpha = 0 is the passive tap with its full footprint; alpha = 1 leaves no
footprint at all, so no detector can beat chance there (by construction).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .channel import cgauss, db_to_lin


@dataclass(frozen=True)
class Stages:
    r_mean: float
    r_var: float
    r_high: float


def stages(alpha: float) -> Stages:
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be in [0, 1], got {alpha}")
    clip = lambda v: float(min(max(v, 0.0), 1.0))
    return Stages(clip(alpha / 0.5), clip((alpha - 0.5) / 0.25), clip((alpha - 0.75) / 0.25))


def make_attack(cfg_attacker: dict, alpha: float, nominal_power: float, start_symbol: int = 0):
    """Return an ``attack(x, rng)`` hook for ``channel.simulate_link``.

    ``nominal_power`` is the untapped signal power at the fiber output (the
    fiber power gain for unit transmit power). Symbols before ``start_symbol``
    pass untouched, so one stream can hold normal windows followed by an attack.
    """
    tau = float(cfg_attacker["tap_fraction"])
    eps = float(cfg_attacker["echo"])
    excess = 1.0 / db_to_lin(float(cfg_attacker["excess_snr_db"]))
    st = stages(alpha)

    def attack(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        y = x.copy()
        u = np.sqrt(1.0 - tau) * x[start_symbol:]
        # higher order: echo, power-normalised so it changes shape, not power
        e = (1.0 - st.r_high) * eps
        if e > 0:
            u = (u + e * np.roll(u, 1)) / np.sqrt(1.0 + e * e)
        # variance: excess noise relative to the tapped signal power
        nv = (1.0 - st.r_var) * excess * (1.0 - tau) * nominal_power
        if nv > 0:
            u = u + cgauss(rng, u.shape, nv)
        # mean: gain so output power = nominal * (1 - tau)^(1 - r_mean)
        p_now = (1.0 - tau) * nominal_power + nv
        p_target = nominal_power * (1.0 - tau) ** (1.0 - st.r_mean)
        y[start_symbol:] = u * np.sqrt(p_target / p_now)
        return y

    return attack
