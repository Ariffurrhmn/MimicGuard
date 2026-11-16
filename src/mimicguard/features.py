"""M3: per-window features (frozen set, Experiment Plan 2026-11-15).

All features are computed from what a receiver actually has: the received
samples and the known pilots. Data symbols are unknown, so EVM is
decision-directed.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from .receiver import estimate_channel

FEATURE_NAMES = (
    "power",          # mean received power
    "evm",            # decision-directed EVM after pilot equalisation (linear)
    "pilot_mag",      # |h_hat|, pilot-correlation magnitude
    "pilot_dphase",   # wrapped change of angle(h_hat) from the previous window
    "amp_var",        # sample variance of |rx|
    "amp_kurt",       # excess kurtosis of |rx|
)

_SQRT_HALF = 1.0 / np.sqrt(2.0)


def _phase_step(h_hat: np.ndarray) -> np.ndarray:
    """Pilot phase change between consecutive windows, wrapped to (-pi, pi].

    The absolute carrier phase is arbitrary and, with laser phase noise, a random
    walk; its increment is stationary. The first window gets 0.
    """
    d = np.angle(h_hat[1:] * np.conj(h_hat[:-1]))
    return np.concatenate([[0.0], d])


def window_features(rx: np.ndarray, n_pilots: int) -> np.ndarray:
    """``rx`` shape (n_windows, window) -> features shape (n_windows, 6)."""
    h_hat = estimate_channel(rx, n_pilots)
    z = rx[:, n_pilots:] / h_hat[:, None]
    decided = (np.sign(z.real) + 1j * np.sign(z.imag)) * _SQRT_HALF
    evm = np.sqrt(np.mean(np.abs(z - decided) ** 2, axis=1))
    amp = np.abs(rx)
    return np.column_stack([
        np.mean(np.abs(rx) ** 2, axis=1),
        evm,
        np.abs(h_hat),
        _phase_step(h_hat),
        np.var(amp, axis=1),
        stats.kurtosis(amp, axis=1),
    ])
