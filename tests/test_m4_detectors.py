"""M4/M5 tests on small synthetic data (fast, no channel simulation)."""

import numpy as np
import pytest

from mimicguard.detectors import REGISTRY, calibrate_threshold, make_detector
from mimicguard.evaluate import _delay

L = 50  # stream length


def _data(shift, n_streams=20, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_streams * L, 6))
    X[:, 0] += shift
    return X


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_detector_runs_and_scores_finite(name):
    d = make_detector(name, seed=0, **({"epochs": 5} if name == "ae" else {}))
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    s = d.score(_data(0.0, 4, 2), L)
    assert s.shape == (4 * L,) and np.all(np.isfinite(s))


@pytest.mark.parametrize("name", ["energy", "pca", "iforest", "lof", "ocsvm", "ae"])
def test_shifted_data_scores_higher(name):
    d = make_detector(name, seed=0, **({"epochs": 30} if name == "ae" else {}))
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    if name == "pca":  # PCA residual only sees off-subspace error; shift all columns jointly
        pass
    a = d.score(_data(0.0, 8, 3), L).mean()
    b = d.score(_data(4.0, 8, 3), L).mean()
    assert b > a


def test_cusum_restarts_each_stream_and_grows_under_drift():
    d = make_detector("cusum")
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    X = _data(0.0, 2, 5)
    X[L:, 0] += 3.0  # second stream drifts
    s = d.score(X, L).reshape(2, L)
    assert s[1].max() > 5 * s[0].max()
    # state restarts: first window of stream 2 does not inherit stream 1's value
    assert s[1, 0] < 5


def test_random_detector_is_data_independent():
    d = make_detector("random", seed=3)
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    assert np.allclose(d.score(_data(0.0, 2), L), d.score(_data(9.0, 2), L))


def test_threshold_quantile_gives_target_far():
    s = np.random.default_rng(0).normal(size=100000)
    thr = calibrate_threshold(s, 0.01)
    assert abs((s > thr).mean() - 0.01) < 0.002


def test_delay_counts_from_onset_and_ignores_pre_onset_alarms():
    onset = 10
    window = np.tile(np.arange(20), 2)
    real = np.repeat([0, 1], 20)
    alarm = np.zeros(40, bool)
    alarm[3] = True            # stream 0: false alarm before onset only
    alarm[20 + 13] = True      # stream 1: detected 3 windows after onset
    frac, delay = _delay(alarm, window, real, onset)
    assert frac == 0.5 and delay == 3.0


def test_spec_parsing_and_names():
    assert make_detector("ae_L2").name == "ae_L2" or make_detector("ae_L2").name == "ae_mlp_L2"
    d = make_detector("pca_drop_evm")
    assert d.name == "pca_drop_evm" and d.keep == [0, 2, 3, 4, 5]
    assert make_detector("lof_cusum").name == "lof_cusum"
    with pytest.raises(ValueError):
        make_detector("pca_drop_nope")


def test_seq_wrapper_accumulates_and_restarts():
    d = make_detector("pca_cusum")
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    X = _data(0.0, 2, 5)
    X[L:, 1:] += 1.5      # stream 2 shifts off the PCA subspace
    s = d.score(X, L).reshape(2, L)
    assert s[1, -1] > 3 * max(s[0].max(), 1.0)
    assert s[1, 0] < s[1, -1]


def test_dropped_feature_is_ignored():
    d = make_detector("energy_drop_evm")
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    X = _data(0.0, 2, 4); Y = X.copy(); Y[:, 1] += 50
    assert np.allclose(d.score(X, L), d.score(Y, L))


def test_context_stacks_previous_windows_within_stream():
    d = make_detector("pca_ctx3")
    X = np.arange(2 * 4 * 6, dtype=float).reshape(8, 6)  # 2 streams of 4 windows
    S = d._stack(X, 4)
    assert S.shape == (8, 18)
    assert np.allclose(S[1, :6], X[1]) and np.allclose(S[1, 6:12], X[0])
    assert np.allclose(S[0, 6:12], X[0])            # first window repeats
    assert np.allclose(S[4, 6:12], X[4])            # stream 2 does not borrow from stream 1


def test_tuned_picks_a_candidate_and_runs():
    from mimicguard.detectors import GRIDS
    d = make_detector("pca_tuned")
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    assert d.choice in GRIDS["pca"]
    assert np.all(np.isfinite(d.score(_data(1.0, 3, 2), L)))


@pytest.mark.parametrize("spec", ["dae", "ae_ctx3", "ocsvm_ctx2", "lof_ctx4_cusum", "pca_drop_evm_ctx2"])
def test_new_specs_build_and_score(spec):
    kw = {"epochs": 3} if spec.startswith(("ae", "dae")) else {}
    d = make_detector(spec, **kw)
    d.fit(_data(0.0), _data(0.0, 8, 1), L)
    assert d.score(_data(0.0, 2, 2), L).shape == (2 * L,)
