import numpy as np
import pytest

from mimicguard import channel, theory
from mimicguard.config import REPO_ROOT, deep_merge, load_config
from mimicguard.modulation import make_frames, qpsk_demodulate, qpsk_modulate
from mimicguard.receiver import bit_error_rate, estimate_channel, evm, receive
from mimicguard.rng import link_streams

BASE = load_config(REPO_ROOT / "experiments" / "configs" / "base.yaml")
IDEAL_FIBER = {"fiber": {"noise_enabled": False, "residual_dispersion_fraction": 0.0,
                         "laser_linewidth_hz": 0.0}}


def cfg_with(**sections):
    return deep_merge(BASE, sections)


def test_qpsk_roundtrip_and_unit_energy():
    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, size=(4, 512), dtype=np.int8)
    s = qpsk_modulate(bits)
    assert np.allclose(np.mean(np.abs(s) ** 2), 1.0)
    assert np.array_equal(qpsk_demodulate(s), bits)


def test_fiber_attenuation_matches_db_per_km():
    f = BASE["fiber"]
    assert channel.fiber_power_gain(f) == pytest.approx(10 ** (-0.2 * 20 / 10))
    x = qpsk_modulate(np.random.default_rng(1).integers(0, 2, 2 * 20000))
    y = channel.fiber(x, deep_merge(f, IDEAL_FIBER["fiber"]), 10e9, np.random.default_rng(2))
    assert np.mean(np.abs(y) ** 2) == pytest.approx(channel.fiber_power_gain(f), rel=1e-9)


def test_dispersion_is_allpass_and_grows_with_length():
    f = BASE["fiber"]
    h = channel.dispersion_transfer(4096, 10e9, f)
    assert np.allclose(np.abs(h), 1.0)
    x = qpsk_modulate(np.random.default_rng(3).integers(0, 2, 2 * 4096))
    evms = []
    for frac in (0.0, 0.05, 1.0, 5.0):
        ff = deep_merge(f, {"residual_dispersion_fraction": frac, "noise_enabled": False,
                            "laser_linewidth_hz": 0.0})
        y = channel.fiber(x, ff, 10e9, np.random.default_rng(0)) / np.sqrt(channel.fiber_power_gain(f))
        evms.append(float(evm(y[None, :], x[None, :])[0]))
    assert evms[0] < 1e-12 and evms == sorted(evms)


def test_fixed_gain_handover_restores_unit_power_and_shows_a_tap():
    cfg = cfg_with(**IDEAL_FIBER, wireless={"fading": "none", "snr_db": 200.0})
    out = channel.simulate_link(cfg, 200, link_streams(0, 0))
    assert np.mean(np.abs(out.rx) ** 2) == pytest.approx(1.0, rel=1e-6)
    tap = lambda x, rng: np.sqrt(0.9) * x  # placeholder for an M2 passive tap
    out_t = channel.simulate_link(cfg, 200, link_streams(0, 0), attack=tap)
    assert np.mean(np.abs(out_t.rx) ** 2) == pytest.approx(0.9, rel=1e-6)


def test_agc_handover_hides_a_tap():
    cfg = cfg_with(**IDEAL_FIBER, handover={"mode": "agc"}, wireless={"fading": "none", "snr_db": 200.0})
    tap = lambda x, rng: np.sqrt(0.9) * x
    out_t = channel.simulate_link(cfg, 200, link_streams(0, 0), attack=tap)
    assert np.mean(np.abs(out_t.rx) ** 2) == pytest.approx(1.0, rel=1e-6)


@pytest.mark.parametrize("fading", ["rayleigh", "rician"])
def test_fading_has_unit_mean_power(fading):
    h = channel.fading_coefficients({"fading": fading, "rician_k": 5.0}, 200_000, np.random.default_rng(5))
    assert np.mean(np.abs(h) ** 2) == pytest.approx(1.0, abs=0.01)


def test_pilot_estimate_converges_at_high_snr():
    cfg = cfg_with(**IDEAL_FIBER, wireless={"fading": "rayleigh", "snr_db": 60.0})
    out = channel.simulate_link(cfg, 100, link_streams(1, 0))
    h_hat = estimate_channel(out.rx, cfg["signal"]["pilot_symbols"])
    assert np.max(np.abs(h_hat - out.h) / np.abs(out.h)) < 0.01


@pytest.mark.parametrize("fading,snr_db", [("none", 6.0), ("rayleigh", 10.0), ("rician", 10.0)])
def test_ber_matches_theory_with_perfect_csi(fading, snr_db):
    cfg = cfg_with(**IDEAL_FIBER, wireless={"fading": fading, "snr_db": snr_db})
    out = channel.simulate_link(cfg, 3000, link_streams(2, 0))
    _, bits_hat, _ = receive(out.rx, cfg["signal"]["pilot_symbols"], h_true=out.h)
    sim = bit_error_rate(out.data_bits, bits_hat)
    ref = float(theory.ber_theory(fading, 10 ** (snr_db / 10), k=5.0))
    assert sim == pytest.approx(ref, rel=0.08)


def test_rician_theory_limits():
    s = np.array([1.0, 10.0, 100.0])
    assert np.allclose(theory.ber_rician(s, 0.0), theory.ber_rayleigh(s), rtol=1e-6)
    assert np.allclose(theory.ber_rician(s, 1e4), theory.ber_awgn(s), rtol=0.05, atol=1e-12)
