"""M5: evaluation of detectors on one grid cell.

Per (detector, alpha) the test stream holds normal windows before the attack
onset and attack windows from it. Metrics:

* ``auc``      ROC AUC, post-onset attack windows vs pre-onset normal windows
* ``pd``       detection probability at the calibrated threshold (attack windows alarmed)
* ``far_test`` empirical false-alarm rate on pre-onset test windows (should be near the target)
* ``det_frac`` share of test streams with at least one alarm after onset
* ``delay``    median windows from onset to first alarm, among detected streams (NaN if none)

The threshold comes from the normal-only validation scores only.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score

from .dataset import CellData
from .detectors import calibrate_threshold, make_detector

DEFAULT_DETECTORS = ("random", "energy", "cusum", "pca", "ocsvm", "iforest", "lof", "ae")


def _delay(alarm: np.ndarray, window: np.ndarray, realisation: np.ndarray, onset: int):
    delays = []
    n_streams = 0
    for r in np.unique(realisation):
        m = realisation == r
        a, w = alarm[m], window[m]
        n_streams += 1
        hit = np.flatnonzero(a & (w >= onset))
        if hit.size:
            delays.append(int(w[hit[0]]) - onset)
    det_frac = len(delays) / max(n_streams, 1)
    return det_frac, (float(np.median(delays)) if delays else float("nan"))


def evaluate_cell(cell: CellData, detectors=DEFAULT_DETECTORS, far: float = 0.01,
                  seed: int = 0, window_len: int | None = None, det_kwargs: dict | None = None) -> list[dict]:
    """Return one record per (detector, alpha)."""
    onset = cell.meta["onset"]
    first = next(iter(cell.test.values()))
    stream_len = int(np.max(first.window)) + 1
    rows = []
    for name in detectors:
        det = make_detector(name, seed=seed, **(det_kwargs or {}).get(name, {}))
        det.fit(cell.X_train, cell.X_val, stream_len)
        thr = calibrate_threshold(det.score(cell.X_val, stream_len), far)
        for alpha, t in cell.test.items():
            s = det.score(t.X, stream_len)
            alarm = s > thr
            normal, attack = t.y == 0, t.y == 1
            keep = normal | attack  # all test windows are one or the other
            auc = float(roc_auc_score(t.y[keep], s[keep]))
            det_frac, delay = _delay(alarm, t.window, t.realisation, onset)
            rows.append({
                "detector": det.name, "alpha": float(alpha),
                "auc": auc, "pd": float(alarm[attack].mean()),
                "far_test": float(alarm[normal].mean()),
                "det_frac": det_frac, "delay": delay,
            })
    return rows
