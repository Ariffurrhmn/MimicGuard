"""v2: correlated fading, footprint variants, fixed-ARL protocol, bootstrap."""

import numpy as np
import pytest

from mimicguard.channel import fading_coefficients, fiber_power_gain
from mimicguard.config import load_config
from mimicguard.v2.data import cell_config, gen_streams
from mimicguard.v2.footprints import KINDS, SCALE_RANGE, build_attack
from mimicguard.v2.protocol import (add_cusum, cp_interval, cusum_transform, equivalence_verdict, evaluate_entry,
                                    hier_boot_diff)

BASE = load_config("experiments/configs/base.yaml")


def test_fading_default_unchanged_and_rho_correlates():
    a = fading_coefficients({"fading": "rayleigh"}, 50, np.random.default_rng(3))
    b = fading_coefficients({"fading": "rayleigh", "rho": 0.0}, 50, np.random.default_rng(3))
    assert np.allclose(a, b)
    h = np.array([fading_coefficients({"fading": "rayleigh", "rho": 0.9}, 300, np.random.default_rng(i)) for i in range(200)])
    assert abs(np.mean(np.abs(h) ** 2) - 1.0) < 0.1
    assert abs(np.mean(h[:, 1:] * np.conj(h[:, :-1])).real - 0.9) < 0.05


@pytest.mark.parametrize("kind", [k for k in KINDS if k != "ladder"])
def test_footprint_restores_power_and_leaves_prefix(kind):
    cfg = cell_config(BASE, "none", 20.0)
    nominal = fiber_power_gain(cfg["fiber"])
    rng = np.random.default_rng(0)
    x = np.sqrt(nominal) * (rng.normal(size=4000) + 1j * rng.normal(size=4000)) / np.sqrt(2)
    lo, hi = SCALE_RANGE[kind]
    atk = build_attack({"kind": kind, "scale": float(np.sqrt(lo * hi))}, cfg["attacker"], nominal, start_symbol=1000)
    y = atk(x, np.random.default_rng(1))
    assert np.allclose(y[:1000], x[:1000])
    assert abs(np.mean(np.abs(y[1000:]) ** 2) / nominal - 1.0) < 0.02
    assert not np.allclose(y[1000:], x[1000:])


def test_gen_streams_shapes_and_roles_disjoint():
    cfg = cell_config(BASE, "rayleigh", 20.0)
    X, iq = gen_streams(cfg, 0, "train", 2, 5, keep_iq=True)
    assert X.shape == (10, 6) and iq.shape == (10, 256)
    X2, _ = gen_streams(cfg, 0, "val", 2, 5)
    assert not np.allclose(X, X2)


def test_cusum_transform_matches_reference():
    s = np.array([[0.0, 1.0, 2.0, 0.0, 0.0]])
    out = cusum_transform(s, 0.0, 1.0, 0.5)
    assert np.allclose(out, [[0.0, 0.5, 2.0, 1.5, 1.0]])


def test_fixed_arl_threshold_holds_on_iid_scores():
    rng = np.random.default_rng(0)
    H = 50

    def ent(n, shift=0.0):
        return rng.normal(size=(n, H)) + shift

    e = {"val": ent(100), "cal": ent(2000), "chk": ent(2000), "test": {"a": np.hstack([ent(300), ent(300, 3.0)])}}
    rows, arr = evaluate_entry(e, onset=H, ps=(0.05,))
    r = rows[0]
    assert abs(r["fa_chk"] - 0.05) < 0.02 and r["fa_lo"] <= r["fa_chk"] <= r["fa_hi"]
    assert r["pd"] > 0.99 and r["auc"] > 0.9
    w = add_cusum(e)
    assert w["test"]["a"].shape == e["test"]["a"].shape


def test_cp_interval_and_equivalence():
    lo, hi = cp_interval(5, 100)
    assert 0.01 < lo < 0.05 < hi < 0.12
    assert equivalence_verdict(-0.01, 0.02, 0.05) == "equivalent"
    assert equivalence_verdict(0.02, 0.1, 0.05) == "different"
    assert equivalence_verdict(-0.03, 0.08, 0.05) == "inconclusive"


def test_hier_boot_detects_a_real_difference():
    rng = np.random.default_rng(0)
    a = (rng.random((5, 200)) < 0.8).astype(float)
    b = (rng.random((5, 200)) < 0.5).astype(float)
    d, lo, hi = hier_boot_diff(a, b, B=300)
    assert lo > 0 and 0.2 < d < 0.4
