"""M1: coherent receiver (pilot channel estimate, one-tap equaliser, decisions)."""

from __future__ import annotations

import numpy as np

from .modulation import pilot_sequence, qpsk_demodulate


def estimate_channel(rx: np.ndarray, n_pilots: int) -> np.ndarray:
    """Least-squares per-window channel estimate from the leading pilots."""
    p = pilot_sequence(n_pilots)
    return (rx[:, :n_pilots] @ p.conj()) / np.vdot(p, p).real


def equalise(rx: np.ndarray, h_hat: np.ndarray) -> np.ndarray:
    return rx / h_hat[:, None]


def receive(rx: np.ndarray, n_pilots: int, h_true: np.ndarray | None = None):
    """Equalise and decide. Uses ``h_true`` (perfect CSI) when given.

    Returns ``(z, bits_hat, h_used)``; ``z`` and ``bits_hat`` cover data symbols only.
    """
    h = h_true if h_true is not None else estimate_channel(rx, n_pilots)
    z = equalise(rx, h)[:, n_pilots:]
    return z, qpsk_demodulate(z), h


def bit_error_rate(bits: np.ndarray, bits_hat: np.ndarray) -> float:
    return float(np.mean(bits != bits_hat))


def evm(z: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """Per-window RMS error vector magnitude (linear, relative to reference power)."""
    return np.sqrt(np.mean(np.abs(z - ref) ** 2, axis=-1) / np.mean(np.abs(ref) ** 2, axis=-1))
