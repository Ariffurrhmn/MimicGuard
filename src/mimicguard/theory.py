"""Closed-form QPSK bit error rates used as M1 sanity references.

SNR here is Es/N0 at the receiver (unit symbol energy, noise variance 1/SNR).
For Gray QPSK each bit sees BER = Q(sqrt(SNR)) = Q(sqrt(2 * gamma_b)) with
gamma_b = SNR / 2. Fading results average over gamma_b (Simon & Alouini MGF form).
"""

from __future__ import annotations

import numpy as np
from scipy import integrate, special


def qfunc(x):
    return 0.5 * special.erfc(np.asarray(x) / np.sqrt(2.0))


def ber_awgn(snr_lin):
    return qfunc(np.sqrt(snr_lin))


def ber_rayleigh(snr_lin):
    gb = np.asarray(snr_lin) / 2.0
    return 0.5 * (1.0 - np.sqrt(gb / (1.0 + gb)))


def _ber_rician_scalar(snr_lin: float, k: float) -> float:
    gb = snr_lin / 2.0

    def mgf(s):  # MGF of the Rician-faded SNR, evaluated at s < 0
        d = 1.0 + k - s * gb
        return (1.0 + k) / d * np.exp(k * s * gb / d)

    val, _ = integrate.quad(lambda t: mgf(-1.0 / np.sin(t) ** 2), 0.0, np.pi / 2)
    return val / np.pi


def ber_rician(snr_lin, k: float):
    return np.vectorize(lambda s: _ber_rician_scalar(float(s), k))(snr_lin)


def ber_theory(fading: str, snr_lin, k: float = 5.0):
    if fading == "none":
        return ber_awgn(snr_lin)
    if fading == "rayleigh":
        return ber_rayleigh(snr_lin)
    if fading == "rician":
        return ber_rician(snr_lin, k)
    raise ValueError(fading)
