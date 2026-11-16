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
