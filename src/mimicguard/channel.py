"""M1: two-segment fiber -> handover -> wireless channel at 1 sample per symbol.

Power convention: the transmitter sends unit average power. On the nominal
(untapped) link the handover restores unit power, so the wireless receiver
sees unit mean signal power and its noise variance is ``1 / SNR``. Fiber
amplifier noise is referenced to the nominal fiber output power, so a tap
lowers the signal but not that noise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

C_M_S = 299_792_458.0


def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 10.0)


def cgauss(rng: np.random.Generator, shape, var: float = 1.0) -> np.ndarray:
    """Circular complex Gaussian with total variance ``var``."""
    s = np.sqrt(var / 2.0)
    return s * (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))


# ---------------------------------------------------------------- fiber
def fiber_power_gain(cfg_fiber: dict) -> float:
    """Linear power gain (<1) from attenuation over the fiber length."""
    return db_to_lin(-cfg_fiber["attenuation_db_per_km"] * cfg_fiber["length_km"])


def dispersion_transfer(n: int, symbol_rate: float, cfg_fiber: dict) -> np.ndarray:
    """All-pass residual chromatic dispersion H(w) = exp(j * beta2/2 * w^2 * L_res)."""
    d_s_m2 = cfg_fiber["dispersion_ps_nm_km"] * 1e-6  # ps/(nm km) -> s/m^2
    lam = cfg_fiber["wavelength_nm"] * 1e-9
    beta2 = -d_s_m2 * lam**2 / (2.0 * np.pi * C_M_S)  # s^2/m
    l_res = cfg_fiber["residual_dispersion_fraction"] * cfg_fiber["length_km"] * 1e3
    w = 2.0 * np.pi * np.fft.fftfreq(n, d=1.0 / symbol_rate)
    return np.exp(1j * 0.5 * beta2 * w**2 * l_res)


def fiber(x: np.ndarray, cfg_fiber: dict, symbol_rate: float, rng: np.random.Generator) -> np.ndarray:
    """Propagate the flat symbol stream ``x`` through the fiber segment."""
    if not cfg_fiber.get("enabled", True):
        return x.copy()
    gain = fiber_power_gain(cfg_fiber)
    y = np.sqrt(gain) * x
    if cfg_fiber["residual_dispersion_fraction"] > 0:
        y = np.fft.ifft(np.fft.fft(y) * dispersion_transfer(y.size, symbol_rate, cfg_fiber))
    lw = cfg_fiber.get("laser_linewidth_hz", 0.0)
    if lw > 0:
        step_var = 2.0 * np.pi * lw / symbol_rate
        y = y * np.exp(1j * np.cumsum(rng.normal(0.0, np.sqrt(step_var), y.size)))
    if cfg_fiber.get("noise_enabled", True):
        y = y + cgauss(rng, y.shape, gain / db_to_lin(cfg_fiber["snr_db"]))
    return y


# ---------------------------------------------------------------- handover
def handover(x: np.ndarray, cfg_handover: dict, nominal_gain: float, window: int) -> np.ndarray:
    """Optical-to-radio conversion. fixed_gain: undo the nominal fiber loss; agc: unit power per window."""
    mode = cfg_handover.get("mode", "fixed_gain")
    if mode == "fixed_gain":
        return x / np.sqrt(nominal_gain)
    if mode == "agc":
        w = x.reshape(-1, window)
        return (w / np.sqrt(np.mean(np.abs(w) ** 2, axis=1, keepdims=True))).ravel()
    raise ValueError(f"unknown handover mode {mode!r}")


# ---------------------------------------------------------------- wireless
def fading_coefficients(cfg_wireless: dict, n_windows: int, rng: np.random.Generator) -> np.ndarray:
    """Block-fading coefficient per window, unit mean power."""
    kind = cfg_wireless.get("fading", "none")
    if kind == "none":
        return np.ones(n_windows, dtype=np.complex128)
    if kind == "rayleigh":
        return cgauss(rng, n_windows, 1.0)
    if kind == "rician":
        k = float(cfg_wireless["rician_k"])
        los_phase = rng.uniform(0, 2 * np.pi)  # fixed per realisation
        return np.sqrt(k / (k + 1)) * np.exp(1j * los_phase) + cgauss(rng, n_windows, 1.0 / (k + 1))
    raise ValueError(f"unknown fading {kind!r}")


def wireless(x_win: np.ndarray, h: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    """y = h * x + n per window; ``x_win`` shape (n_windows, window)."""
    return h[:, None] * x_win + cgauss(rng, x_win.shape, 1.0 / db_to_lin(snr_db))


# ---------------------------------------------------------------- full link
Attack = Callable[[np.ndarray, np.random.Generator], np.ndarray]


@dataclass
class LinkOutput:
    tx: np.ndarray            # (n_windows, window) transmitted symbols
    data_bits: np.ndarray     # (n_windows, 2 * n_data)
    rx: np.ndarray            # (n_windows, window) wireless receiver samples
    h: np.ndarray             # (n_windows,) wireless fading coefficients
    meta: dict = field(default_factory=dict)


def simulate_link(cfg: dict, n_windows: int, rngs: dict[str, np.random.Generator],
                  attack: Attack | None = None) -> LinkOutput:
    """Run one channel realisation.

    ``rngs`` needs keys ``bits``, ``fiber``, ``fading``, ``wireless`` (and
    ``attack`` when an attack is given). ``attack`` acts on the flat stream
    at the fiber output, before the handover (M2 hook).
    """
    from .modulation import make_frames

    sig = cfg["signal"]
    window, n_pil, rs = sig["window_symbols"], sig["pilot_symbols"], sig["symbol_rate_baud"]
    tx, bits = make_frames(rngs["bits"], n_windows, window, n_pil)

    flat = fiber(tx.ravel(), cfg["fiber"], rs, rngs["fiber"])
    nominal = fiber_power_gain(cfg["fiber"]) if cfg["fiber"].get("enabled", True) else 1.0
    if attack is not None:
        flat = attack(flat, rngs["attack"])
    radio = handover(flat, cfg["handover"], nominal, window).reshape(n_windows, window)

    h = fading_coefficients(cfg["wireless"], n_windows, rngs["fading"])
    rx = wireless(radio, h, cfg["wireless"]["snr_db"], rngs["wireless"])
    return LinkOutput(tx=tx, data_bits=bits, rx=rx, h=h, meta={"fiber_gain": nominal})
