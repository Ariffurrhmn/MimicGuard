import numpy as np
import pytest

from mimicguard.attacker import make_attack, stages
from mimicguard.channel import fiber_power_gain, simulate_link
from mimicguard.config import REPO_ROOT, deep_merge, load_config
from mimicguard.dataset import generate_cell, split_realisations
from mimicguard.features import FEATURE_NAMES, window_features
from mimicguard.rng import link_streams

BASE = load_config(REPO_ROOT / "experiments" / "configs" / "base.yaml")
NOM = fiber_power_gain(BASE["fiber"])
W = BASE["signal"]["window_symbols"]
NP = BASE["signal"]["pilot_symbols"]


def run(alpha, fading="none", snr_db=30.0, n=400, onset=0):
    cfg = deep_merge(BASE, {"wireless": {"fading": fading, "snr_db": snr_db}})
    atk = None if alpha is None else make_attack(cfg["attacker"], alpha, NOM, start_symbol=onset * W)
    return simulate_link(cfg, n, link_streams(0, 0, "t"), attack=atk)


def test_stage_schedule():
    assert stages(0.0) == stages(0.0) and stages(0.0).r_mean == 0.0
    s = stages(0.25); assert (s.r_mean, s.r_var, s.r_high) == (0.5, 0.0, 0.0)
    s = stages(0.5); assert (s.r_mean, s.r_var, s.r_high) == (1.0, 0.0, 0.0)
    s = stages(0.75); assert (s.r_mean, s.r_var, s.r_high) == (1.0, 1.0, 0.0)
    s = stages(1.0); assert (s.r_mean, s.r_var, s.r_high) == (1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        stages(1.5)


def test_alpha_one_leaves_no_footprint():
    normal, attacked = run(None), run(1.0)
    assert np.allclose(normal.rx, attacked.rx, atol=1e-12)


def test_power_footprint_follows_mean_stage():
    p_norm = np.mean(np.abs(run(None).rx) ** 2)
    ratios = [np.mean(np.abs(run(a).rx) ** 2) / p_norm for a in (0.0, 0.25, 0.5)]
    assert ratios[0] == pytest.approx(0.9, abs=0.01)
    assert ratios[1] == pytest.approx(0.9 ** 0.5, abs=0.01)
    assert ratios[2] == pytest.approx(1.0, abs=0.01)


def test_evm_footprint_shrinks_with_alpha():
    evm = {a: np.mean(window_features(run(a).rx, NP)[:, FEATURE_NAMES.index("evm")])
           for a in (None, 0.5, 0.75, 1.0)}
    assert evm[0.5] > evm[0.75] > evm[1.0]
    assert evm[1.0] == pytest.approx(evm[None])


def test_attack_onset_leaves_earlier_windows_untouched():
    normal, attacked = run(None), run(0.0, onset=200)
    assert np.allclose(normal.rx[:200], attacked.rx[:200])
    assert not np.allclose(normal.rx[200:], attacked.rx[200:])


def test_feature_shapes_and_finite():
    f = window_features(run(0.0, fading="rayleigh", snr_db=10.0, n=50).rx, NP)
    assert f.shape == (50, len(FEATURE_NAMES)) and np.all(np.isfinite(f))


def test_split_is_disjoint_and_sized():
    sp = split_realisations(BASE, seed=3)
    allr = np.concatenate(list(sp.values()))
    assert len(sp["train"]) == 30 and len(sp["val"]) == 10 and len(sp["test"]) == 10
    assert len(np.unique(allr)) == 50


def test_cell_attacks_only_in_test_and_paired_across_alpha():
    small = deep_merge(BASE, {"split": {"realisations": 10}, "dataset": {"windows_per_realisation": 20,
                                                                        "attack_onset_window": 10}})
    cell = generate_cell(small, seed=0, fading="rician", snr_db=15.0, alphas=[0.0, 1.0])
    assert cell.X_train.shape == (6 * 20, 6) and cell.X_val.shape == (2 * 20, 6)
    t0, t1 = cell.test[0.0], cell.test[1.0]
    assert t0.y.sum() == 2 * 10
    pre = t0.y == 0
    assert np.allclose(t0.X[pre], t1.X[pre])          # same normal windows across alpha
    # alpha = 1 attack windows equal the normal stream of the same realisation
    normal_like = generate_cell(small, seed=0, fading="rician", snr_db=15.0, alphas=[1.0]).test[1.0]
    assert np.allclose(normal_like.X, t1.X)
