"""Data generation for v2: normal streams for training / validation / calibration / checking, attacked test streams.

Streams of ``H`` windows are used for everything that is normal-only, so the calibration horizon and the pre-onset
span of a test stream are the same (``H`` windows). Test streams hold ``n_test_win`` windows with the attack from
window ``onset``. Roles use disjoint realisation index ranges, so no stream is ever shared between roles.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..channel import fiber_power_gain, simulate_link
from ..config import deep_merge
from ..features import window_features
from ..rng import link_streams
from .footprints import build_attack

ROLE_OFFSET = {"train": 0, "val": 10_000, "cal": 20_000, "chk": 30_000, "test": 40_000, "otrain": 50_000,
               "match": 60_000, "match_test": 70_000}


def _one(args):
    cfg, seed, fading, r, n_win, spec, onset, keep_iq = args
    if "OMP_NUM_THREADS" not in os.environ:
        os.environ["OMP_NUM_THREADS"] = "1"
    rngs = link_streams(seed, int(r), "fading", fading)
    attack = None
    if spec is not None and spec.get("kind") == "onoff":
        spec = {**spec, "window_symbols": cfg["signal"]["window_symbols"]}
    if spec is not None:
        nominal = fiber_power_gain(cfg["fiber"]) if cfg["fiber"].get("enabled", True) else 1.0
        attack = build_attack(spec, cfg["attacker"], nominal, start_symbol=onset * cfg["signal"]["window_symbols"])
    out = simulate_link(cfg, n_win, rngs, attack=attack)
    feats = window_features(out.rx, cfg["signal"]["pilot_symbols"])
    return feats, (out.rx.astype(np.complex64) if keep_iq else None)


def cell_config(base: dict, fading: str, snr_db: float, rho: float = 0.0) -> dict:
    return deep_merge(base, {"wireless": {"fading": fading, "snr_db": float(snr_db), "rho": float(rho)}})


def gen_streams(cfg: dict, seed: int, role: str, n: int, n_win: int, spec: dict | None = None, onset: int = 0,
                n_jobs: int = 1, keep_iq: bool = False):
    """Return ``(X, iq)``: features ``(n * n_win, 6)`` and, if requested, complex samples ``(n * n_win, window)``.

    ``spec`` is an attacker footprint spec or None for normal streams; the attack starts at window ``onset``.
    """
    fading = cfg["wireless"]["fading"]
    jobs = [(cfg, seed, fading, ROLE_OFFSET[role] + i, n_win, spec, onset, keep_iq) for i in range(n)]
    if n_jobs > 1 and n > 1:
        with ProcessPoolExecutor(max_workers=n_jobs) as ex:
            res = list(ex.map(_one, jobs, chunksize=max(1, n // (4 * n_jobs))))
    else:
        res = [_one(j) for j in jobs]
    X = np.vstack([r[0] for r in res])
    iq = np.vstack([r[1] for r in res]) if keep_iq else None
    return X, iq


def make_cell_data(base: dict, seed: int, fading: str, snr_db: float, sizes: dict, test_specs: dict,
                   n_jobs: int = 1, keep_iq: bool = False, rho: float = 0.0, otrain_spec: dict | None = None) -> dict:
    """All data for one (seed, fading, SNR) cell.

    ``sizes``: n_train, n_val, n_cal, n_chk, n_test, H (normal-stream length), n_test_win, onset.
    ``test_specs``: label -> footprint spec; one attacked test set is generated per label.
    ``otrain_spec``: if given, attacked training streams (attack from window 0) for supervised oracles.
    """
    cfg = cell_config(base, fading, snr_db, rho)
    H, onset, ntw = int(sizes["H"]), int(sizes["onset"]), int(sizes["n_test_win"])
    d = {"cfg": cfg, "H": H, "onset": onset, "n_test_win": ntw, "iq": {}}
    for role in ("train", "val", "cal", "chk"):
        X, iq = gen_streams(cfg, seed, role, int(sizes["n_" + role]), H, None, 0, n_jobs, keep_iq)
        d["X_" + role] = X
        if keep_iq:
            d["iq"][role] = iq
    d["test"], d["test_iq"] = {}, {}
    for label, spec in test_specs.items():
        X, iq = gen_streams(cfg, seed, "test", int(sizes["n_test"]), ntw, spec, onset, n_jobs, keep_iq)
        d["test"][label] = X
        if keep_iq:
            d["test_iq"][label] = iq
    if otrain_spec is not None:
        X, iq = gen_streams(cfg, seed, "otrain", int(sizes["n_otrain"]), H, otrain_spec, 0, n_jobs, keep_iq)
        d["X_otrain"] = X
        if keep_iq:
            d["iq"]["otrain"] = iq
    return d
