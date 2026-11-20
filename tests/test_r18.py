import numpy as np

from mimicguard.v2.r18 import head_transform


def test_warmup_is_silent_and_affine_invariant():
    rng = np.random.default_rng(0)
    s = rng.normal(size=(6, 60))
    a = head_transform(s, 10, 0.0, 0.0)
    assert np.all(a[:, :10] == 0.0)
    assert np.all(a >= 0.0)
    b = head_transform(3.0 * s + 7.0, 10, 0.0, 0.0)   # a shift and rescale of the score changes nothing
    assert np.allclose(a, b, atol=1e-9)
    z1 = head_transform(s, 10, 0.05, None)
    z2 = head_transform(3.0 * s + 7.0, 10, 0.05, None)
    assert np.allclose(z1, z2, atol=1e-9)


def test_tracking_absorbs_a_persistent_step_but_fixed_baseline_does_not():
    s = np.r_[np.zeros(30), 5.0 * np.ones(70)][None, :] + 0.01 * np.random.default_rng(1).normal(size=(1, 100))
    fixed = head_transform(s, 20, 0.0, None)
    track = head_transform(s, 20, 0.2, None)
    assert fixed[0, -1] > 50 and track[0, -1] < 5
