"""M1: QPSK mapping and window/pilot layout."""

from __future__ import annotations

import numpy as np

_SQRT_HALF = 1.0 / np.sqrt(2.0)


def qpsk_modulate(bits: np.ndarray) -> np.ndarray:
    """Gray-mapped QPSK with unit average energy. ``bits`` shape (..., 2*n)."""
    b = np.asarray(bits, dtype=np.int8).reshape(*bits.shape[:-1], -1, 2)
    return ((1 - 2 * b[..., 0]) + 1j * (1 - 2 * b[..., 1])) * _SQRT_HALF


def qpsk_demodulate(symbols: np.ndarray) -> np.ndarray:
    """Hard decisions back to bits, shape (..., 2*n)."""
    out = np.empty((*symbols.shape, 2), dtype=np.int8)
    out[..., 0] = symbols.real < 0
    out[..., 1] = symbols.imag < 0
    return out.reshape(*symbols.shape[:-1], -1)


def pilot_sequence(n_pilots: int) -> np.ndarray:
    """Fixed, known pilot block (same for every window). Seeded independently of runs."""
    rng = np.random.default_rng(20261115)
    return qpsk_modulate(rng.integers(0, 2, size=2 * n_pilots))


def make_frames(rng: np.random.Generator, n_windows: int, window: int, n_pilots: int):
    """Transmit symbols laid out as (n_windows, window): pilots first, then data.

    Returns ``(tx, data_bits)`` where ``data_bits`` has shape
    (n_windows, 2 * (window - n_pilots)).
    """
    n_data = window - n_pilots
    data_bits = rng.integers(0, 2, size=(n_windows, 2 * n_data), dtype=np.int8)
    tx = np.empty((n_windows, window), dtype=np.complex128)
    tx[:, :n_pilots] = pilot_sequence(n_pilots)
    tx[:, n_pilots:] = qpsk_modulate(data_bits)
    return tx, data_bits
